from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend import crud
from backend.models import User
from backend.schemas.user import UserUpdate


class UserService:
    """Административное управление пользователями."""

    def __init__(self, db: Session):
        self.db = db

    def list_users(self) -> list[User]:
        return crud.get_all_users(self.db)

    def update(self, user_id: int, data: UserUpdate) -> User:
        if crud.get_user_by_id(self.db, user_id) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        try:
            return crud.update_user(self.db, user_id, **data.model_dump(exclude_unset=True))
        except ValueError as exc:  # неизвестная роль
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
