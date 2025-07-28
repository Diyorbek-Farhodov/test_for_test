from pydantic import BaseModel
from typing import Optional

class OptionOut(BaseModel):
    option: str
    text: Optional[str] = None

class QuestionTestOut(BaseModel):
    savol: int
    question_id: int
    text: str
    options: list[OptionOut]
    correct_option: Optional[str] = None