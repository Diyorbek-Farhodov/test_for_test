from fastapi import APIRouter

from .test_random import router as random_router

from .upload_test import router as test_router_upload
from .subject import router as subject_router
from .submit_test import router as submit_test_router
from .create_question_image import router as image_test_router

test_router = APIRouter(prefix='/test', tags=['Test'])



test_router.include_router(random_router)
test_router.include_router(test_router_upload)
test_router.include_router(subject_router)
test_router.include_router(submit_test_router)
test_router.include_router(image_test_router)