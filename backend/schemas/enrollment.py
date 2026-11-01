from pydantic import BaseModel, ConfigDict

class EnrollmentRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    model_config = ConfigDict(from_attributes=True)