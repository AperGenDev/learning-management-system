from pydantic import BaseModel, EmailStr, Field, ConfigDict
from backend.schemas.role import RoleRead

class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=6)
    role_name: str = "student"
    model_config = ConfigDict(
        extra="forbid",                  # лишние поля → 422
        str_strip_whitespace=True,       # обрезать пробелы
        json_schema_extra={
            "examples": [
                {"full_name": "Иван Иванов", "email": "ivan@example.com",
                 "password": "secret123", "role_name": "student"}
            ]
        },
    )



class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: RoleRead                       # ← вложенный объект
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6)
    role_name: str | None = None

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)