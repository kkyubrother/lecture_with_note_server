from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from google.auth.transport import requests as google_requests
from google.oauth2.id_token import verify_oauth2_token

from sqlalchemy.ext.asyncio import AsyncSession

from lecture_with_note_server.security import create_jwt_token
from lecture_with_note_server.database.base import get_session
from lecture_with_note_server.service import get_user_by_email
from lecture_with_note_server.service import add_user


router = APIRouter(prefix="/login")


class GoogleLoginRequest(BaseModel):
    token: str


@router.post("/google")
async def login_google(token: GoogleLoginRequest, session: AsyncSession = Depends(get_session)):
    requests = google_requests.Request()

    try:
        # Verify the token and get the user's Google profile
        google_profile = verify_oauth2_token(token.token, requests)
        email = google_profile['email']
        name = google_profile['name']

        try:
            user = await get_user_by_email(session, "google", email)
        except IndexError:
            user = await add_user(session, "google", email)
            await session.commit()

        response = JSONResponse(jsonable_encoder({"email": email, "name": name}))

        session_id = create_jwt_token(user.id)
        response.set_cookie("session_id", session_id, expires=google_profile["exp"], httponly=True)

        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Bad Request")

    except Exception as e:
        return {"error": str(e)}


@router.post("/logout")
async def login_google():
    response = JSONResponse(jsonable_encoder({"message": "ok"}))
    response.delete_cookie("session_id")

    return response
