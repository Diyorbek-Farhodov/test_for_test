import json

from fastapi import Body, APIRouter, HTTPException
from pydantic import BaseModel

from src.api.v1.test.test_random import DATA_FILE
from src.schema.submit_test import TestSubmission, TestResultOut

router = APIRouter()

@router.post("/submit-test/{subject_id}", response_model=TestResultOut)
async def submit_test(subject_id: int, submission: TestSubmission = Body(...)):
    # Test sessiyasini yuklab olish
    if not DATA_FILE.exists():
        raise HTTPException(status_code=400, detail="Test sessiyasi topilmadi")

    test_sessions_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    session_questions = test_sessions_data.get(str(subject_id))

    if not session_questions:
        raise HTTPException(status_code=404, detail="Ushbu fan uchun test sessiyasi topilmadi")

    answers_dict = {a.question_id: a.selected_option for a in submission.answers}

    correct = 0
    incorrect = 0

    for q in session_questions:
        q_id = q["question_id"]
        correct_option = q["correct_option"]
        selected_option = answers_dict.get(q_id)

        if selected_option is None:
            incorrect += 1  # Javob bermagan
        elif selected_option == correct_option:
            correct += 1
        else:
            incorrect += 1

    return TestResultOut(
        student_id=submission.student_id,
        total_questions=len(session_questions),
        correct_answers=correct,
        incorrect_answers=incorrect
    )
