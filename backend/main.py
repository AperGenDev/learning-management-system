from fastapi import FastAPI

from backend.database import Base, engine
from backend.api import auth, courses

Base.metadata.create_all(bind=engine)   # для лабы ок; при наличии alembic можно убрать

app = FastAPI(title="LMS API", version="1.0")

app.include_router(auth.router)
app.include_router(courses.router)