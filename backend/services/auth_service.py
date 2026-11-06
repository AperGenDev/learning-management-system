from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend import crud
from backend.models import User
from backend.schemas.auth import Token
from backend.schemas.user import UserCreate
from backend.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: UserCreate) -> User:
        if crud.get_user_by_email(self.db, data.email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
        try:
            return crud.create_user(
                self.db,
                full_name=data.full_name,
                email=data.email,
                password_hash=hash_password(data.password),
                role_name=data.role_name,
            )
        except ValueError as exc:  # неизвестная роль
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    def login(self, email: str, password: str) -> Token:
        user = crud.get_user_by_email(self.db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "User is blocked")
        role_name = user.role.name if user.role else None
        return Token(access_token=create_access_token(subject=user.email, role=role_name))
