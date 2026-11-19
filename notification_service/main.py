import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from notification_service import config
from notification_service.connections import ConnectionManager
from notification_service.consumer import consume

logging.basicConfig(level=logging.INFO, format="%(asctime)s [NOTIFY] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("notify")

manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(consume(manager))  # слушаем RabbitMQ в фоне
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="Notification Service", lifespan=lifespan)


def user_id_from_token(token: str) -> int | None:
    """Тот же JWT, что выдаёт API Service при /login. Из него берём id пользователя."""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    except JWTError:
        return None
    uid = payload.get("uid")
    return int(uid) if uid is not None else None


@app.get("/health")
def health():
    return {"status": "ok", "online_users": manager.online_users()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    user_id = user_id_from_token(token)
    if user_id is None:
        log.info("× отклонено подключение с неверным токеном")
        await websocket.close(code=1008)  # 1008 = policy violation
        return

    await manager.connect(user_id, websocket)
    await websocket.send_json({
        "event": "connected",
        "title": "Подключено",
        "text": "Вы будете получать уведомления о ваших курсах",
    })
    try:
        while True:
            await websocket.receive_text()  # держим соединение открытым
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
