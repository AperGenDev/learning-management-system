from pydantic import BaseModel, Field, ConfigDict

class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class CategoryRead(BaseModel):
    id: int
    name: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)