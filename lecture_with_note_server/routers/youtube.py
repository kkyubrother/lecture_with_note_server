from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends

from pydantic import BaseModel

from lecture_with_note_server.security import get_current_uid
from lecture_with_note_server.utils.youtube_data import get_youtube_video_title_from_video_id
from lecture_with_note_server.utils.config import load_google_api_key


router = APIRouter(prefix="/youtube")
api_key = load_google_api_key()


class YoutubeVideoId(BaseModel):
    video_id: str


@router.get("")
async def get_video_title(video_id: str, _: str = Depends(get_current_uid)):
    try:
        return get_youtube_video_title_from_video_id(video_id)
    except ValueError:
        raise HTTPException(400, "youtube.bad_request")
