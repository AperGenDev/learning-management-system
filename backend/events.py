import json
import logging
from datetime import datetime, timezone

import pika
from pika.exceptions import AMQPError

log = logging.getLogger("lms.events")


class EventPublisher:
    def __init__(self, url: str, exchange: str):
        self.url = url
        self.exchange = exchange

    def _parameters(self) -> pika.URLParameters:
        params = pika.URLParameters(self.url)
        params.connection_attempts = 1
        params.socket_timeout = 2
        return params

    def publish(self, event: str, recipients: list[int], **data) -> bool:
        message = {
            "event": event,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "recipients": sorted(set(recipients)),
            "data": data,
        }
        body = json.dumps(message, ensure_ascii=False).encode("utf-8")
        try:
            connection = pika.BlockingConnection(self._parameters())
            try:
                channel = connection.channel()
                # topic-обменник: сообщения маршрутизируются по routing key (= типу события)
                channel.exchange_declare(exchange=self.exchange, exchange_type="topic", durable=True)
                channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=event,
                    body=body,
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,  # сообщение сохраняется на диск брокера
                    ),
                )
            finally:
                connection.close()
        except (AMQPError, OSError) as exc:
            log.warning("× не удалось опубликовать событие %s: %s", event, exc)
            return False

        log.info("→ RabbitMQ [%s] получатели=%s данные=%s", event, message["recipients"], data)
        return True
