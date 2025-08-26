import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.base.db import get_db
from src.model import Question, Subject

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

async def save_upload_file(upload_file: UploadFile) -> str:
    if not upload_file:
        return None
    ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as buffer:
        buffer.write(await upload_file.read())
    return filepath

@router.post("/create-question-with-images")
async def create_question_with_images(
    subject_id: int = Form(...),
    text: str = Form(None),
    image: UploadFile = File(None),
    option_a: str = Form(None),
    option_a_image: UploadFile = File(None),
    option_b: str = Form(None),
    option_b_image: UploadFile = File(None),
    option_c: str = Form(None),
    option_c_image: UploadFile = File(None),
    option_d: str = Form(None),
    option_d_image: UploadFile = File(None),
    correct_option_text: str = Form(...),
    correct_option_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    # Fan mavjudligini tekshirish
    subject = await db.scalar(select(Subject).where(Subject.id == subject_id))
    if not subject:
        raise HTTPException(status_code=404, detail=f"Subject ID {subject_id} topilmadi")

    # Fayllarni saqlash
    image_path = await save_upload_file(image)
    option_a_img_path = await save_upload_file(option_a_image)
    option_b_img_path = await save_upload_file(option_b_image)
    option_c_img_path = await save_upload_file(option_c_image)
    option_d_img_path = await save_upload_file(option_d_image)
    correct_option_img_path = await save_upload_file(correct_option_image)
    # Savol obyektini yaratish
    question = Question(
        text=text,
        question_image=image_path,
        option_a=option_a,
        option_a_image=option_a_img_path,
        option_b=option_b,
        option_b_image=option_b_img_path,
        option_c=option_c,
        option_c_image=option_c_img_path,
        option_d=option_d,
        option_d_image=option_d_img_path,
        correct_option_text=correct_option_text,
        correct_option_image = correct_option_img_path,
        subject_id=subject_id
    )

    db.add(question)
    await db.commit()
    await db.refresh(question)

    return {
        "message": "Savol muvaffaqiyatli qo‘shildi",
        "question_id": question.id
    }
