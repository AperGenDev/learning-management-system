from pydantic import BaseModel, Field, ConfigDict

class ModuleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    order_num: int = Field(ge=1)
    content: str | None = None
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class ModuleRead(BaseModel):
    id: int
    course_id: int
    title: str
    order_num: int
    content: str | None
    model_config = ConfigDict(from_attributes=True)

class ModuleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    order_num: int | None = Field(default=None, ge=1)
    content: str | None = None
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)