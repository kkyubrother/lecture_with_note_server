import jwt

from fastapi import Cookie
from fastapi import HTTPException

from lecture_with_note_server.utils.config import load_secret_key


SECRET_KEY = load_secret_key()


def create_jwt_token(user_id: int) -> str:
    payload = {"sub": user_id}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def get_current_uid(session_id: str = Cookie(None)):
    try:
        payload = jwt.decode(session_id, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except (jwt.PyJWTError, KeyError) as e:
        raise HTTPException(status_code=401, detail="Unauthorized")
