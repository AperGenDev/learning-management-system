"""Получить рекомендации на стороне API Service

1. Берём из БД курсы студента, каталог и число студентов на каждом курсе.
2. Отправляем эти данные по gRPC в Recommendation Service (отдельный процесс).
3. Получаем id рекомендованных курсов и дополняем их данными из БД.
"""
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend import crud
from backend.config import setting
from backend.models import Course, User
from backend.recommendation_client import (
    CourseInfo, RecommendationClient, RecommendationUnavailable,
)

log = logging.getLogger("lms.recommendations")


class RecommendationService:
    def __init__(self, db: Session, client: RecommendationClient | None = None):
        self.db = db
        self.client = client or RecommendationClient(setting.RECOMMENDATION_HOST, setting.RECOMMENDATION_PORT)

    @staticmethod
    def _info(course: Course, counts: dict[int, int]) -> CourseInfo:
        return CourseInfo(id=course.id, category_id=course.category_id, students_count=counts.get(course.id, 0))

    def for_student(self, student: User, limit: int = 5) -> list[dict]:
        counts = crud.get_course_student_counts(self.db)
        enrolled = [self._info(c, counts) for c in crud.get_my_courses(self.db, student.id)]
        candidates = [self._info(c, counts) for c in crud.get_courses_catalog(self.db)]

        log.info("-> gRPC GetRecommendations(student_id=%s, записан на %s, кандидатов %s) → %s",
                 student.id, [c.id for c in enrolled], len(candidates), self.client.target)
        try:
            items = self.client.get_recommendations(student.id, enrolled, candidates, limit)
        except RecommendationUnavailable as exc:
            log.warning("× сервис рекомендаций недоступен: %s", exc)
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Recommendation service is unavailable")
        log.info("<- gRPC ответ: %s", [(i.course_id, i.score) for i in items])

        courses = crud.get_courses_by_ids(self.db, [i.course_id for i in items])
        return [
            {"course": courses[i.course_id], "score": i.score, "reason": i.reason}
            for i in items if i.course_id in courses
        ]
