from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend import crud
from backend.models import Course, Module, User
from backend.schemas.course import CourseCreate, CourseUpdate
from backend.schemas.module import ModuleCreate, ModuleUpdate

from backend.config import setting
from backend.events import EventPublisher

class CourseService:
    def __init__(self, db: Session):
        self.db = db
        self.publisher = EventPublisher(
            setting.RABBITMQ_URL,
            setting.EVENTS_EXCHANGE
        )


    @staticmethod
    def _is_admin(user: User) -> bool:
        return user.role is not None and user.role.name == "admin"

    def _check_owner(self, course: Course, user: User) -> None:
        """Менять курс и его модули может только автор курса или администратор."""
        if course.author_id != user.id and not self._is_admin(user):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not the author")

    def _check_category(self, category_id: int | None) -> None:
        if category_id is not None and crud.get_category_by_id(self.db, category_id) is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category not found")

    def list_catalog(self, category_id: int | None = None) -> list[Course]:
        return crud.get_courses_catalog(self.db, category_id)

    def list_by_author(self, user: User) -> list[Course]:
        return crud.get_courses_by_author(self.db, user.id)

    def get(self, course_id: int) -> Course:
        course = crud.get_course_by_id(self.db, course_id)
        if not course:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
        return course

    def create(self, data: CourseCreate, author_id: int) -> Course:
        self._check_category(data.category_id)
        return crud.create_course(
            self.db,
            title=data.title,
            author_id=author_id,
            description=data.description,
            category_id=data.category_id,
            is_published=data.is_published,
        )

    def update(self, course_id: int, data: CourseUpdate, user: User) -> Course:
        course = self.get(course_id)
        self._check_owner(course, user)
        fields = data.model_dump(exclude_unset=True)
        if "category_id" in fields:
            self._check_category(fields["category_id"])
        return crud.update_course(self.db, course_id, **fields)

    def delete(self, course_id: int, user: User) -> None:
        course = self.get(course_id)
        self._check_owner(course, user)
        crud.delete_course(self.db, course_id)

    def can_edit(self, course: Course, user: User | None) -> bool:
        return user is not None and (course.author_id == user.id or self._is_admin(user))


    def list_modules(self, course_id: int) -> list[Module]:
        self.get(course_id)  
        return crud.get_modules_by_course(self.db, course_id)

    def _get_module(self, course_id: int, module_id: int) -> Module:
        module = crud.get_module_by_id(self.db, module_id)
        if module is None or module.course_id != course_id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Module not found")
        return module

    def add_module(self, course_id: int, data: ModuleCreate, user: User) -> Module:
        course = self.get(course_id)
        self._check_owner(course, user)

        try:
            module = crud.create_module(
                self.db,
                course_id=course_id,
                title=data.title,
                order_num=data.order_num,
                content=data.content,
            )
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Module with order_num={data.order_num} already exists in this course",
            )

        recipients = crud.get_student_ids_of_course(self.db, course_id)

        self.publisher.publish(
            event="module.added",
            recipients=recipients,
            course_id=course.id,
            course_title=course.title,
            module_id=module.id,
            module_title=module.title,
        )

        return module

    def update_module(self, course_id: int, module_id: int, data: ModuleUpdate, user: User) -> Module:
        course = self.get(course_id)
        self._check_owner(course, user)
        self._get_module(course_id, module_id)
        try:
            return crud.update_module(self.db, module_id, **data.model_dump(exclude_unset=True))
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Module with this order_num already exists")

    def delete_module(self, course_id: int, module_id: int, user: User) -> None:
        course = self.get(course_id)
        self._check_owner(course, user)
        self._get_module(course_id, module_id)
        crud.delete_module(self.db, module_id)


    def enroll(self, course_id: int, student: User):
        """Сценарий 4: запись студента на опубликованный курс."""
        course = self.get(course_id)
        if not course.is_published:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Course is not published")
        enrollment = crud.enroll_student(self.db, student_id=student.id, course_id=course_id)
        if enrollment is None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Already enrolled")
        return enrollment

    def is_enrolled(self, course_id: int, student: User | None) -> bool:
        return student is not None and crud.get_enrollment(self.db, student.id, course_id) is not None

    def my_courses(self, student: User) -> list[Course]:
        return crud.get_my_courses(self.db, student.id)

    def students(self, course_id: int, user: User) -> list[User]:
        course = self.get(course_id)
        self._check_owner(course, user)
        return crud.get_students_of_course(self.db, course_id)
