from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend import crud
from backend.models import Category
from backend.schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[Category]:
        return crud.get_all_categories(self.db)

    def create(self, data: CategoryCreate) -> Category:
        if crud.get_category_by_name(self.db, data.name):
            raise HTTPException(status.HTTP_409_CONFLICT, "Category already exists")
        return crud.create_category(self.db, name=data.name, description=data.description)
