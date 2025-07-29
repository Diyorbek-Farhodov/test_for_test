from pydantic import BaseModel
from typing import List, Optional

class AnswerItem(BaseModel):
    question_id: int
    selected_option: Optional[str]  # A, B, C, D yoki None

class TestSubmission(BaseModel):
    student_id: str
    answers: List[AnswerItem]

class TestResultOut(BaseModel):
    student_id: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int