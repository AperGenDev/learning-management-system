from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend import crud
from backend.schemas.course import CourseCreate, CourseUpdate

class CourseService:
    def __init__(self, db: Session):
        self.db = db

    def list_catalog(self, category_id: int | None = None):
        return crud.get_courses_catalog(self.db, category_id)

    def get(self, course_id: int):
        course = crud.get_course_by_id(self.db, course_id)
        if not course:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
        return course

    def create(self, data: CourseCreate, author_id: int):
        return crud.create_course(
            self.db,
            title=data.title,
            author_id=author_id,
            description=data.description,
            category_id=data.category_id,
            is_published=data.is_published,
        )

    def update(self, course_id: int, data: CourseUpdate, user):
        course = self.get(course_id)
        if course.author_id != user.id and user.role.name != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the author")
        fields = data.model_dump(exclude_unset=True)
        return crud.update_course(self.db, course_id, **fields)

    def delete(self, course_id: int, user):
        course = self.get(course_id)
        if course.author_id != user.id and user.role.name != "admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the author")
        crud.delete_course(self.db, course_id)