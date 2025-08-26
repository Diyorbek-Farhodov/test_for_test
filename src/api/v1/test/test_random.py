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
        answer_texts = [
            {"text": q.option_a, "image": getattr(q, "option_a_image", None)},
            {"text": q.option_b, "image": getattr(q, "option_b_image", None)},
            {"text": q.option_c, "image": getattr(q, "option_c_image", None)},
            {"text": q.option_d, "image": getattr(q, "option_d_image", None)},
        ]

        # Bazadagi to‘g‘ri javobni olish (matn yoki rasm bo‘lishi mumkin)
        correct_answer_original = {
            "text": q.correct_option_text,
            "image": getattr(q, "correct_option_image", None)
        }

        # Variantlarni aralashtirish
        random.shuffle(answer_texts)

        # Option harflarini berish
        options = [
            OptionOut(option="A", text=answer_texts[0]["text"], image=answer_texts[0]["image"]),
            OptionOut(option="B", text=answer_texts[1]["text"], image=answer_texts[1]["image"]),
            OptionOut(option="C", text=answer_texts[2]["text"], image=answer_texts[2]["image"]),
            OptionOut(option="D", text=answer_texts[3]["text"], image=answer_texts[3]["image"]),
        ]

        # Aralashgan ro‘yxatda to‘g‘ri javobni topish
        correct_option = None
        for letter, opt in zip(["A", "B", "C", "D"], options):
            if opt.text == correct_answer_original["text"] and opt.image == correct_answer_original["image"]:
                correct_option = letter
                break

        if not correct_option:
            raise HTTPException(
                status_code=500,
                detail=f"Savol ID {q.id} uchun to‘g‘ri javob topilmadi"
            )

        question_out = QuestionTestOut(
            savol=idx,
            question_id=q.id,
            text=q.text,
            img=getattr(q, "img", None),  # rasm majburiy emas
            options=options,
            correct_option=correct_option
        )

        response.append(question_out)
        session_data.append(question_out.model_dump())


    # Test sessiyasini saqlash
    test_sessions[str(subject_id)] = session_data

    # Faylga yozish
    DATA_FILE.write_text(json.dumps(test_sessions, indent=4, ensure_ascii=False))

    return response