"""Алгоритм подбора курсов. 
  1. Курсы, на которые студент уже записан, не предлагаем.
  2. Если категория курса совпадает с категориями курсов студента 
     курс получает +10 баллов за каждое совпадение (интерес к теме).
  3. Популярность: +1 балл за каждого записанного студента.
  4. Если студент ещё никуда не записан (холодный старт) 
     рекомендуем самые популярные курсы
"""

from collections import Counter
from dataclasses import dataclass

CATEGORY_WEIGHT = 10.0
POPULARITY_WEIGHT = 1.0


@dataclass(frozen=True)
class Course:
    id: int
    category_id: int  # 0 без категории
    students_count: int


@dataclass(frozen=True)
class Recommendation:
    course_id: int
    score: float
    reason: str


def recommend(enrolled: list[Course], candidates: list[Course], limit: int) -> list[Recommendation]:
    enrolled_ids = {c.id for c in enrolled} #множество id курсов, на которые студент записан
    #сколько курсов студента в каждой категории
    interests = Counter(c.category_id for c in enrolled if c.category_id)

    result: list[Recommendation] = []
    for course in candidates:
        if course.id in enrolled_ids:
            continue

        matches = interests.get(course.category_id, 0) if course.category_id else 0
        score = matches * CATEGORY_WEIGHT + course.students_count * POPULARITY_WEIGHT

        if matches:
            reason = f"Та же тема, что и у {matches} из ваших курсов"
        elif course.students_count:
            reason = f"Популярный курс: записано студентов - {course.students_count}"
        else:
            reason = "Новый курс в каталоге"

        result.append(Recommendation(course_id=course.id, score=score, reason=reason))

    result.sort(key=lambda r: (-r.score, r.course_id))
    return result[:limit] if limit > 0 else result
