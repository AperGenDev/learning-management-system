from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend import crud
from backend.security import decode_token
from backend.services.auth_service import AuthService
from backend.services.course_service import CourseService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ─── 1. Сессия БД на один запрос ───
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─── 2. Сервисы (получают сессию через DI) ───
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_course_service(db: Session = Depends(get_db)) -> CourseService:
    return CourseService(db)

# ─── 3. Текущий пользователь (JWT) ───
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            raise creds_exc
    except JWTError:
        raise creds_exc

    user = crud.get_user_by_email(db, email)
    if not user:
        raise creds_exc
    return user

# ─── 4. Проверка роли ───
def require_role(*allowed: str):
    def checker(user=Depends(get_current_user)):
        if not user.role or user.role.name not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker