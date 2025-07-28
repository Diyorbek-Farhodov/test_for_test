from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.db import get_db
from src.model import Subject
from src.schema.subject import SubjectOut, SubjectCreate

router = APIRouter()

@router.post("/subject_name", response_model=SubjectOut, status_code=201)
async def create_subject(subject_in: SubjectCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Subject).where(Subject.name == subject_in.name)
    )
    if existing.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu fan allaqachon mavjud."
        )

    new_subject = Subject(name=subject_in.name)
    db.add(new_subject)
    await db.commit()
    await db.refresh(new_subject)
    return new_subject
