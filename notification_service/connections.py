"""Реестр WebSocket-подключений: какой пользователь через какие сокеты подключён."""
import logging
from collections import defaultdict

from fastapi import WebSocket

log = logging.getLogger("notify")


class ConnectionManager:
    def __init__(self) -> None:
        # Один пользователь может быть подключён с нескольких вкладок/клиентов.
        self._clients: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients[user_id].add(websocket)
        log.info("+ пользователь %s подключился (онлайн: %s)", user_id, self.online_users())

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self._clients.get(user_id)
        if sockets is None:
            return
        sockets.discard(websocket)
        if not sockets:
            del self._clients[user_id]
        log.info("- пользователь %s отключился (онлайн: %s)", user_id, self.online_users())

    def online_users(self) -> list[int]:
        return sorted(self._clients)

    async def send(self, user_id: int, payload: dict) -> int:
        """Отправить уведомление всем сокетам пользователя. Возвращает число доставок."""
        delivered = 0
        for websocket in list(self._clients.get(user_id, ())):
            try:
                await websocket.send_json(payload)
                delivered += 1
            except Exception:  # клиент «отвалился», а disconnect ещё не сработал
                self.disconnect(user_id, websocket)
        return delivered
