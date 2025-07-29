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

    # Savollarni random tanlash
    selected_questions = random.sample(questions, min(len(questions), 25))

    response = []
    session_data = []

    for idx, q in enumerate(selected_questions, 1):
        # Javob matnlarini ro'yxatga yig'ish
        answer_texts = [q.option_a, q.option_b, q.option_c, q.option_d]

        # Matnlarni aralashtirib yuborish
        random.shuffle(answer_texts)

        # Option harflari doim A, B, C, D bo'ladi, lekin matnlar aralashgan
        options = [
            OptionOut(option="A", text=answer_texts[0]),
            OptionOut(option="B", text=answer_texts[1]),
            OptionOut(option="C", text=answer_texts[2]),
            OptionOut(option="D", text=answer_texts[3]),
        ]

        # To'g'ri javobni topish (aralashgan matnlar ichidan)
        if q.correct_option == answer_texts[0]:
            correct_answer = "A"
        elif q.correct_option == answer_texts[1]:
            correct_answer = "B"
        elif q.correct_option == answer_texts[2]:
            correct_answer = "C"
        else:
            correct_answer = "D"

        question_out = QuestionTestOut(
            savol=idx,
            question_id=q.id,
            text=q.text,
            options=options,
            correct_option=correct_answer  # Endi harf (A, B, C, D) qaytaradi
        )

        response.append(question_out)
        session_data.append(question_out.model_dump())

    # Test sessiyasini saqlash
    test_sessions[str(subject_id)] = session_data

    # Faylga yozish
    DATA_FILE.write_text(json.dumps(test_sessions, indent=4, ensure_ascii=False))

    return response