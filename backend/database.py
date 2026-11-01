from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import setting


DATABASE_URL = (
    f"postgresql+psycopg2://{setting.DB_USER}:{setting.DB_PASSWORD}"
    f"@{setting.DB_HOST}:{setting.DB_PORT}/{setting.DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass