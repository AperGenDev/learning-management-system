from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from backend import crud
from backend.database import SessionLocal
from backend.models import User
from backend.security import decode_token
from backend.services.auth_service import AuthService
from backend.services.category_service import CategoryService
from backend.services.course_service import CourseService
from backend.services.recommendation_service import RecommendationService
from backend.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


#1. Сессия БД на один запрос
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. Сервисы (получают сессию через DI)
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_course_service(db: Session = Depends(get_db)) -> CourseService:
    return CourseService(db)


def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    return CategoryService(db)


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    return RecommendationService(db)


# 3.Текущий пользователь (JWT)
def user_from_token(db: Session, token: str | None) -> User | None:
    """Достаёт пользователя по JWT. Используется и REST API, и веб-интерфейсом."""
    if not token:
        return None
    try:
        email = decode_token(token).get("sub")
    except JWTError:
        return None
    if not email:
        return None
    user = crud.get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    user = user_from_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# 4.Проверка роли
def require_role(*allowed: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if not user.role or user.role.name not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker
