from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.deps import get_auth_service, get_current_user
from backend.models import User
from backend.schemas.auth import Token
from backend.schemas.user import UserCreate, UserRead
from backend.services.auth_service import AuthService

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, svc: AuthService = Depends(get_auth_service)):
    return svc.register(data)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          svc: AuthService = Depends(get_auth_service)):
    # В поле username передаётся email (так устроена стандартная форма OAuth2)
    return svc.login(form.username, form.password)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return user
