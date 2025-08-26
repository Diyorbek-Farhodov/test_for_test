from fastapi import APIRouter
from .sutdent_login import router as student_login_router

login_router = APIRouter(prefix="/login",tags=['Login'])



login_router.include_router(student_login_router)
