from fastapi import APIRouter, Depends

from backend.api.deps import get_course_service, get_current_user, require_role
from backend.models import User
from backend.schemas.course import CourseCreate, CourseRead, CourseUpdate
from backend.schemas.enrollment import EnrollmentRead
from backend.schemas.module import ModuleCreate, ModuleRead, ModuleUpdate
from backend.schemas.user import UserRead
from backend.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


# ─── курсы ───
@router.get("/", response_model=list[CourseRead])
def catalog(category_id: int | None = None,
            svc: CourseService = Depends(get_course_service)):
    return svc.list_catalog(category_id)


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, svc: CourseService = Depends(get_course_service)):
    return svc.get(course_id)


@router.post("/", response_model=CourseRead, status_code=201)
def create_course(data: CourseCreate,
                  svc: CourseService = Depends(get_course_service),
                  user: User = Depends(require_role("teacher", "admin"))):
    return svc.create(data, author_id=user.id)


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(course_id: int, data: CourseUpdate,
                  svc: CourseService = Depends(get_course_service),
                  user: User = Depends(get_current_user)):
    return svc.update(course_id, data, user)


@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int,
                  svc: CourseService = Depends(get_course_service),
                  user: User = Depends(get_current_user)):
    svc.delete(course_id, user)


# ─── модули курса ───
@router.get("/{course_id}/modules", response_model=list[ModuleRead])
def list_modules(course_id: int,
                 svc: CourseService = Depends(get_course_service),
                 _: User = Depends(get_current_user)):
    return svc.list_modules(course_id)


@router.post("/{course_id}/modules", response_model=ModuleRead, status_code=201)
def create_module(course_id: int, data: ModuleCreate,
                  svc: CourseService = Depends(get_course_service),
                  user: User = Depends(require_role("teacher", "admin"))):
    return svc.add_module(course_id, data, user)


@router.patch("/{course_id}/modules/{module_id}", response_model=ModuleRead)
def update_module(course_id: int, module_id: int, data: ModuleUpdate,
                  svc: CourseService = Depends(get_course_service),
                  user: User = Depends(require_role("teacher", "admin"))):
    return svc.update_module(course_id, module_id, data, user)


@router.delete("/{course_id}/modules/{module_id}", status_code=204)
def delete_module(course_id: int, module_id: int,
                  svc: CourseService = Depends(get_course_service),
                  user: User = Depends(require_role("teacher", "admin"))):
    svc.delete_module(course_id, module_id, user)


# ─── запись на курс ───
@router.post("/{course_id}/enroll", response_model=EnrollmentRead, status_code=201)
def enroll(course_id: int,
           svc: CourseService = Depends(get_course_service),
           user: User = Depends(require_role("student"))):
    return svc.enroll(course_id, user)


@router.get("/{course_id}/students", response_model=list[UserRead])
def course_students(course_id: int,
                    svc: CourseService = Depends(get_course_service),
                    user: User = Depends(require_role("teacher", "admin"))):
    return svc.students(course_id, user)
