from fastapi import APIRouter, Depends

from backend.api.deps import get_category_service, require_role
from backend.models import User
from backend.schemas.category import CategoryCreate, CategoryRead
from backend.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(svc: CategoryService = Depends(get_category_service)):
    return svc.list_all()


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(data: CategoryCreate,
                    svc: CategoryService = Depends(get_category_service),
                    _: User = Depends(require_role("admin"))):
    return svc.create(data)
