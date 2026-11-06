import logging

from fastapi import FastAPI

from backend.api import auth, categories, courses, recommendations, users

logging.basicConfig(level=logging.INFO, format="%(asctime)s [API] %(message)s", datefmt="%H:%M:%S")

app = FastAPI(title="LMS API", version="3.0")

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(categories.router)
app.include_router(users.router)
app.include_router(recommendations.router)
