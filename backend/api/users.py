from fastapi import APIRouter, Depends

from backend.api.deps import get_course_service, get_user_service, require_role
from backend.models import User
from backend.schemas.course import CourseRead
from backend.schemas.user import UserRead, UserUpdate
from backend.services.course_service import CourseService
from backend.services.user_service import UserService

router = APIRouter(tags=["users"])


@router.get("/me/courses", response_model=list[CourseRead])
def my_courses(svc: CourseService = Depends(get_course_service),
               user: User = Depends(require_role("student"))):
    """Раздел «Мои курсы» студента."""
    return svc.my_courses(user)


@router.get("/users", response_model=list[UserRead])
def list_users(svc: UserService = Depends(get_user_service),
               _: User = Depends(require_role("admin"))):
    return svc.list_users()


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, data: UserUpdate,
                svc: UserService = Depends(get_user_service),
                _: User = Depends(require_role("admin"))):
    return svc.update(user_id, data)
