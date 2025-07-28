from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from openpyxl import load_workbook
import io
import random

from src.base.db import get_db
from src.model import Question

router = APIRouter()

@router.post("/upload-questions/")
async def upload_questions(
    subject_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Faqat Excel fayllar qabul qilinadi (.xlsx, .xls)")

    try:
        contents = await file.read()
        workbook = load_workbook(filename=io.BytesIO(contents), data_only=True)
        sheet = workbook.active
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel faylni o‘qib bo‘lmadi: {e}")

    added_count = 0
    errors = []

    option_positions = ['A', 'B', 'C', 'D']  # To‘g‘ri javob qaysi pozitsiyada turishi kerak

    async with db.begin():
        try:
            for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    if len(row) < 5 or any(cell is None for cell in row[:5]):
                        errors.append(f"{row_num}-qatorda barcha 5 ustun to‘ldirilmagan")
                        continue

                    question_text = str(row[0]).strip()
                    correct_text = str(row[1]).strip()
                    wrong_answers = [str(row[2]).strip(), str(row[3]).strip(), str(row[4]).strip()]
                    random.shuffle(wrong_answers)

                    # Har bir savol uchun to‘g‘ri javob pozitsiyasi belgilanadi
                    correct_letter = option_positions[(row_num - 2) % 4]  # 0 -> A, 1 -> B, 2 -> C, 3 -> D

                    options = {}
                    wrong_index = 0
                    for letter in option_positions:
                        if letter == correct_letter:
                            options[letter] = correct_text
                        else:
                            options[letter] = wrong_answers[wrong_index]
                            wrong_index += 1

                    question = Question(
                        text=question_text,
                        option_a=options['A'],
                        option_b=options['B'],
                        option_c=options['C'],
                        option_d=options['D'],
                        correct_option=correct_letter,
                        subject_id=subject_id
                    )
                    db.add(question)
                    added_count += 1

                except Exception as e:
                    errors.append(f"{row_num}-qatorda xatolik: {str(e)}")
                    continue

            await db.commit()

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Bazada xatolik: {e}")

    return {
        "success": added_count,
        "errors": errors if errors else None,
        "message": f"{added_count} ta savol muvaffaqiyatli yuklandi."
    }
