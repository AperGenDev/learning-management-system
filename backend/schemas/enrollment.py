from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnrollmentRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    status: str
    enrolled_at: datetime
    model_config = ConfigDict(from_attributes=True)
