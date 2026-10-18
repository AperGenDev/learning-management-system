from fastapi import APIRouter, Depends

from backend.schemas.course import CourseCreate, CourseRead, CourseUpdate
from backend.schemas.module import ModuleCreate, ModuleRead
from backend.services.course_service import CourseService
from backend.api.deps import get_course_service, require_role, get_current_user
from backend import crud
from backend.database import SessionLocal
from sqlalchemy.orm import Session
from backend.api.deps import get_db

router = APIRouter(prefix="/courses", tags=["courses"])

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
                  user=Depends(require_role("teacher", "admin"))):
    return svc.create(data, author_id=user.id)

@router.patch("/{course_id}", response_model=CourseRead)
def update_course(course_id: int, data: CourseUpdate,
                  svc: CourseService = Depends(get_course_service),
                  user=Depends(get_current_user)):
    return svc.update(course_id, data, user)

@router.delete("/{course_id}", status_code=204)
def delete_course(course_id: int,
                  svc: CourseService = Depends(get_course_service),
                  user=Depends(get_current_user)):
    svc.delete(course_id, user)

# ─── модули курса ───
@router.get("/{course_id}/modules", response_model=list[ModuleRead])
def list_modules(course_id: int, db: Session = Depends(get_db),
                 _=Depends(get_current_user)):
    return crud.get_modules_by_course(db, course_id)

@router.post("/{course_id}/modules", response_model=ModuleRead, status_code=201)
def create_module(course_id: int, data: ModuleCreate,
                  svc: CourseService = Depends(get_course_service),
                  db: Session = Depends(get_db),
                  user=Depends(require_role("teacher", "admin"))):
    svc.get(course_id)                    # 404 если нет
    return crud.create_module(db, course_id=course_id,
                              title=data.title, order_num=data.order_num,
                              content=data.content)