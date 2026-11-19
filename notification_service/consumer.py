import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError

from notification_service import config
from notification_service.connections import ConnectionManager
from notification_service.messages import build_notification

log = logging.getLogger("notify")


async def handle_message(body: bytes, manager: ConnectionManager) -> None:
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        log.warning("пропущено некорректное сообщение: %r", body[:200])
        return

    notification = build_notification(event)
    recipients = event.get("recipients", [])
    log.info("← RabbitMQ событие [%s] для пользователей %s", event.get("event"), recipients)

    for user_id in recipients:
        delivered = await manager.send(user_id, notification)
        if delivered:
            log.info("  → WebSocket: пользователю %s доставлено «%s»", user_id, notification["text"])
        else:
            log.info("  · пользователь %s не в сети, уведомление не доставлено", user_id)


async def _connect() -> AbstractRobustConnection:
    """RabbitMQ может стартовать дольше сервиса (особенно в Docker) — ждём его."""
    while True:
        try:
            return await aio_pika.connect_robust(config.RABBITMQ_URL)
        except (AMQPConnectionError, OSError) as exc:
            log.warning("RabbitMQ недоступен (%s), повтор через 3 с...", exc)
            await asyncio.sleep(3)


async def consume(manager: ConnectionManager) -> None:
    connection = await _connect()
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            config.EVENTS_EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(config.QUEUE_NAME, durable=True)
        await queue.bind(exchange, routing_key="#")
        log.info("Подписка оформлена: обменник '%s' → очередь '%s'", config.EVENTS_EXCHANGE, config.QUEUE_NAME)

        async with queue.iterator() as messages:
            message: AbstractIncomingMessage
            async for message in messages:
                # process() подтверждает (ack) сообщение после успешной обработки
                async with message.process(requeue=False):
                    await handle_message(message.body, manager)
