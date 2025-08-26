from pydantic import BaseModel


class StudentInfo(BaseModel):
    first_name: str = None
    last_name: str = None
    full_name: str = None
    student_id_number: str = None
    group: str = None
    faculty: str = None
    university: str = None

