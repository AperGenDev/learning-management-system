from pydantic import BaseModel, ConfigDict

class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)