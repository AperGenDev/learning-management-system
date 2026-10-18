from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.schemas.user import UserCreate, UserRead
from backend.schemas.auth import Token
from backend.services.auth_service import AuthService
from backend.api.deps import get_auth_service

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, svc: AuthService = Depends(get_auth_service)):
    return svc.register(data)

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          svc: AuthService = Depends(get_auth_service)):
    return svc.login(form.username, form.password)