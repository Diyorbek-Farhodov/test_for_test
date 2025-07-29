from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openpyxl import load_workbook
import io

from src.base.db import get_db
from src.model import Question, Subject

router = APIRouter()


@router.post("/upload-questions/{subject_id}")
async def upload_questions(
        subject_id: int = Path(..., description="Subject ID raqami", gt=0),
        file: UploadFile = File(..., description="Excel fayl (.xlsx, .xls)"),
        db: AsyncSession = Depends(get_db)
):
    # Fayl formatini tekshirish
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Faqat Excel fayllar qabul qilinadi (.xlsx, .xls)")

    # Subject mavjudligini tekshirish
    subject = await db.scalar(select(Subject).where(Subject.id == subject_id))
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} topilmadi")

    # Excel faylni o'qish
    try:
        contents = await file.read()
        workbook = load_workbook(filename=io.BytesIO(contents), data_only=True)
        sheet = workbook.active
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel faylni o'qishda xatolik: {e}")

    added_count = 0
    errors = []

    # Ma'lumotlarni bazaga saqlash
    try:
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Bo'sh qatorlarni o'tkazib yuborish
                if not row or all(cell is None or str(cell).strip() == '' for cell in row[:5]):
                    continue

                # Kamida 5 ta ustun borligini tekshirish
                if len(row) < 5:
                    errors.append(f"Qator {row_num}: Kamida 5 ta ustun bo'lishi kerak")
                    continue

                # Ma'lumotlarni olish
                question_text = str(row[0]).strip() if row[0] is not None else ""
                option_a = str(row[1]).strip() if row[1] is not None else ""
                option_b = str(row[2]).strip() if row[2] is not None else ""
                option_c = str(row[3]).strip() if row[3] is not None else ""
                option_d = str(row[4]).strip() if row[4] is not None else ""

                # Bo'sh maydonlarni tekshirish
                if not all([question_text, option_a, option_b, option_c, option_d]):
                    errors.append(f"Qator {row_num}: Barcha maydonlar to'ldirilishi kerak")
                    continue

                # To'g'ri javobni belgilash (birinchi variant to'g'ri deb hisoblanadi)
                correct_option = option_a

                # Savolni yaratish va bazaga qo'shish
                question = Question(
                    text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_option=correct_option,
                    subject_id=subject_id
                )

                db.add(question)
                added_count += 1

            except Exception as e:
                errors.append(f"Qator {row_num}: {str(e)}")

        # O'zgarishlarni saqlash
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Bazaga saqlashda xatolik: {str(e)}")

    return {
        "message": f"{added_count} ta savol muvaffaqiyatli yuklandi",
        "success_count": added_count,
        "errors": errors,
        "subject_id": subject_id
    }