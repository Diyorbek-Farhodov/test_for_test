import httpx
import logging
from fastapi import HTTPException, APIRouter
from src.base.config import settings
from src.schema.login import LoginRequest

logger = logging.getLogger(__name__)



router = APIRouter()


async def hemis_login(username: str, password: str) -> str:

    try:
        login = int(username.strip())
    except ValueError:
        raise HTTPException(400, "Username raqam bo'lishi kerak")

    payload = {"login": login, "password": password.strip()}
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.HEMIS_LOGIN_URL,
                json=payload,
                headers=headers
            )

            logger.info(f"Login Response Status: {response.status_code}")
            logger.debug(f"Login attempt for user: {login}")

            response.raise_for_status()
            data = response.json()

            token = data.get("data", {}).get("token")
            if not token:
                raise HTTPException(400, "Token topilmadi")

            return token

    except httpx.HTTPStatusError as e:
        logger.error(f"HEMIS login error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 401:
            raise HTTPException(401, "Login yoki parol xato")
        elif e.response.status_code == 400:
            raise HTTPException(400, "Noto'g'ri so'rov ma'lumotlari")
        elif e.response.status_code >= 500:
            raise HTTPException(503, "HEMIS serveri vaqtinchalik ishlamayapti")
        else:
            raise HTTPException(e.response.status_code, f"HEMIS xatoligi: {e.response.text}")
    except httpx.TimeoutException:
        logger.error("HEMIS login timeout")
        raise HTTPException(504, "So'rov vaqti tugadi")
    except httpx.RequestError as e:
        logger.error(f"HEMIS connection error: {e}")
        raise HTTPException(503, "HEMIS serveriga ulanib bo'lmadi")

async def get_student_data(token: str) -> dict:

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(settings.HEMIS_USER_URL, headers=headers)

            logger.info(f"User Data Response Status: {response.status_code}")

            response.raise_for_status()
            data = response.json()

            return data.get("data", {})

    except httpx.HTTPStatusError as e:
        logger.error(f"HEMIS user data error: {e.response.status_code}")
        if e.response.status_code == 401:
            raise HTTPException(401, "Token yaroqsiz yoki muddati tugagan")
        elif e.response.status_code == 403:
            raise HTTPException(403, "Ma'lumotlarga ruxsat yo'q")
        elif e.response.status_code >= 500:
            raise HTTPException(503, "HEMIS serveri vaqtinchalik ishlamayapti")
        else:
            raise HTTPException(e.response.status_code, f"Ma'lumot olishda xatolik: {e.response.text}")
    except httpx.TimeoutException:
        logger.error("HEMIS user data timeout")
        raise HTTPException(504, "So'rov vaqti tugadi")
    except httpx.RequestError as e:
        logger.error(f"HEMIS user data connection error: {e}")
        raise HTTPException(503, "HEMIS serveriga ulanib bo'lmadi")


def format_student_info(raw_data: dict) -> dict:


    if not raw_data:
        return {}

    return {
        "first_name": raw_data.get("first_name", "").strip() or None,
        "last_name": raw_data.get("second_name", "").strip() or None,
        "third_name": raw_data.get("third_name", "").strip() or None,
        "full_name": raw_data.get("full_name", "").strip() or None,
        "student_id": raw_data.get("student_id_number", "").strip() or None,
        "group": raw_data.get("group", {}).get("name") if raw_data.get("group") else None,
        "faculty": raw_data.get("faculty", {}).get("name") if raw_data.get("faculty") else None,
        "university": raw_data.get("university", "").strip() or None,
        "specialty": raw_data.get("specialty", {}).get("name") if raw_data.get("specialty") else None,
        "phone": raw_data.get("phone", "").strip() or None,
        "semester": raw_data.get("semester", {}).get("name") if raw_data.get("semester") else None,
    }


async def get_student_info(username: str, password: str) -> dict:

    token = await hemis_login(username, password)
    raw_data = await get_student_data(token)
    return format_student_info(raw_data)


@router.post("/test-login")
async def test_hemis_login(credentials: LoginRequest):
    try:
        token = await hemis_login(credentials.username, credentials.password)
        return {
            "success": True,
            "message": "Login muvaffaqiyatli!",
            "token_length": len(token),
            "token_preview": token[:20] + "..." if len(token) > 20 else token
        }
    except HTTPException as e:
        return {
            "success": False,
            "error": e.detail,
            "status_code": e.status_code
        }


@router.post("/get-student-info")
async def get_student_info_endpoint(credentials: LoginRequest):
    try:
        student_info = await get_student_info(credentials.username, credentials.password)
        return {
            "success": True,
            "message": "Ma'lumotlar muvaffaqiyatli olindi",
            "data": student_info
        }
    except HTTPException as e:
        return {
            "success": False,
            "error": e.detail,
            "status_code": e.status_code
        }