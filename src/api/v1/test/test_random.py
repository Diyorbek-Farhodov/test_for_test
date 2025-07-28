import random
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.db import get_db
from src.model import Question
from src.schema.questions import QuestionTestOut, OptionOut

router = APIRouter()

test_sessions = {}

DATA_FILE = Path("test_results.json")


@router.get("/get-random-questions-by-subject/{subject_id}", response_model=list[QuestionTestOut])
async def get_random_questions_by_subject(subject_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Question).where(Question.subject_id == subject_id)
    )
    questions = result.scalars().all()

    if not questions:
        raise HTTPException(status_code=404, detail="Bu fan uchun savollar topilmadi")

    selected_questions = random.sample(questions, min(len(questions), 25))

    response = []
    session_data = []

    for idx, q in enumerate(selected_questions, 1):
        options = [
            OptionOut(option="A", text=q.option_a),
            OptionOut(option="B", text=q.option_b),
            OptionOut(option="C", text=q.option_c),
            OptionOut(option="D", text=q.option_d),
        ]
        random.shuffle(options)

        question_out = QuestionTestOut(
            savol=idx,
            question_id=q.id,
            text=q.text,
            options=options,
            correct_option=q.correct_option
        )

        response.append(question_out)

        session_data.append(question_out.model_dump())

    test_sessions[str(subject_id)] = session_data

    DATA_FILE.write_text(json.dumps(test_sessions, indent=4, ensure_ascii=False))

    return response
