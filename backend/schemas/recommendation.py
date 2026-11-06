from pydantic import BaseModel

from backend.schemas.course import CourseRead


class RecommendationRead(BaseModel):
    course: CourseRead
    score: float
    reason: str
