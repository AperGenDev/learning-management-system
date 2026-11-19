import argparse
import asyncio
import json
from datetime import datetime

import requests
import websockets
from websockets.exceptions import InvalidHandshake, WebSocketException


def login(api_url: str, email: str, password: str) -> str:
    try:
        response = requests.post(
            f"{api_url}/login", data={"username": email, "password": password}, timeout=5
        )
    except requests.RequestException as exc:
        raise SystemExit(f"API Service недоступен ({api_url}): {exc}")
    if response.status_code != 200:
        raise SystemExit(f"Не удалось войти: {response.status_code} {response.text}")
    return response.json()["access_token"]


def show(notification: dict) -> None:
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [!] {notification.get('title', '')}: {notification.get('text', '')}", flush=True)


async def listen(ws_url: str, token: str) -> None:
    url = f"{ws_url}/ws?token={token}"
    while True:
        try:
            async with websockets.connect(url) as websocket:
                print(f"Подключено к {ws_url}. Ожидаю уведомления (Ctrl+C — выход)...", flush=True)
                async for raw in websocket:
                    show(json.loads(raw))
        except InvalidHandshake as exc:
            raise SystemExit(f"Сервер отклонил подключение (токен неверный или устарел): {exc}")
        except (OSError, WebSocketException) as exc:
            print(f"Соединение потеряно ({exc}). Переподключение через 3 с...", flush=True)
            await asyncio.sleep(3)


def main() -> None:
    parser = argparse.ArgumentParser(description="Клиент уведомлений LMS")
    parser.add_argument("--email", default="student@example.com")
    parser.add_argument("--password", default="student123")
    parser.add_argument("--api", default="http://localhost:8000", help="адрес API Service")
    parser.add_argument("--ws", default="ws://localhost:8001", help="адрес Notification Service")
    args = parser.parse_args()

    token = login(args.api, args.email, args.password)
    print(f"Вход выполнен: {args.email}")
    try:
        asyncio.run(listen(args.ws, token))
    except KeyboardInterrupt:
        print("\nКлиент остановлен.")


if __name__ == "__main__":
    main()
