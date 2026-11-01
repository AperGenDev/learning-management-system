from pydantic import BaseModel, Field, ConfigDict

class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = None
    is_published: bool = False
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class CourseRead(BaseModel):
    id: int
    title: str
    description: str | None
    author_id: int
    category_id: int | None
    is_published: bool
    model_config = ConfigDict(from_attributes=True)

class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    category_id: int | None = None
    is_published: bool | None = None
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)