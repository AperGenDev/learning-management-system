import os

from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://lms:lms@localhost:5672/")
EVENTS_EXCHANGE = os.getenv("EVENTS_EXCHANGE", "lms.events")
QUEUE_NAME = os.getenv("NOTIFICATION_QUEUE", "notifications")

# Тот же секрет, что у API Service: им проверяется JWT при подключении по WebSocket.
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

if not SECRET_KEY:
    raise RuntimeError("Не задан SECRET_KEY (скопируйте .env.example в .env)")
