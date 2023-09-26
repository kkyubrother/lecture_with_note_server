from typing import Optional

from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from lecture_with_note_server.routers import login
from lecture_with_note_server.routers import youtube

from lecture_with_note_server.security import get_current_uid
from lecture_with_note_server.database.base import init_models
from lecture_with_note_server.database.base import get_session

from lecture_with_note_server import service


class NewLectureRequest(BaseModel):
    title: str
    url: str


class NewNoteRequest(BaseModel):
    data: str
    indexed_playtime: Optional[int]


app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login.router, prefix="/api")
app.include_router(youtube.router, prefix="/api")


@app.on_event("startup")
async def setup_db():
    await init_models()


@app.get("/")
async def root():
    # response = Response()
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/api/protected")
def protected(uid: int = Depends(get_current_uid)):
    return {"message": f"You are authorized, {uid}"}


@app.get("/api/lecture")
async def get_lecture_by_url(url: str, _: str = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):
    try:
        lecture = await service.get_lecture_by_url(session, url)
    except IndexError:
        raise HTTPException(404, "lecture.not_exist")
    return {
        "id": lecture.id,
        "title": lecture.title,
        "url": lecture.url,
    }


@app.delete("/api/lecture")
async def del_lecture_by_url(url: str, uid: int = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):
    try:
        await service.del_lecture(session, uid, url)
    except IndexError:
        raise HTTPException(404, "lecture.not_exist")

    await session.commit()

    return {"message": "ok"}


@app.get("/api/lecture/all")
async def get_lectures(uid: int = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):
    try:
        lectures = await service.get_lectures_by_uid(session, uid)
    except IndexError:
        raise HTTPException(404, "lecture.not_exist")

    result = []
    for lecture in lectures:
        title = lecture.title

        result.append({
            "id": lecture.id,
            "title": title,
            "url": lecture.url,
        })

    return result


@app.post("/api/lecture")
async def post_lecture(data: NewLectureRequest, uid: int = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):
    try:
        await service.get_lecture_by_url(session, data.url)
        raise HTTPException(400, "lecture.exist")
    except IndexError:
        lecture = await service.add_lecture(session, uid, data.url, data.title)
        await session.commit()

    return {
        "id": lecture.id,
        "title": lecture.title,
        "url": lecture.url,
    }


@app.get("/api/lecture/{lecture_id}/note")
async def get_lecture_note(lecture_id: int, uid: int = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):
    try:
        await service.get_lecture(session, lecture_id)
    except IndexError:
        raise HTTPException(404, "lectures.not_exist")

    try:
        note = await service.get_note_by_user_lecture_id(session, uid, lecture_id)
    except IndexError:
        raise HTTPException(404, "notes.not_exist")

    return {
        "id": note.id,
        "data": note.data,
        "indexed_playtime": note.indexed_playtime,
    }


@app.post("/api/lecture/{lecture_id}/note")
async def post_lecture_note(
        lecture_id: int, data: NewNoteRequest,
        uid: int = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):
    try:
        await service.get_lecture(session, lecture_id)
    except IndexError:
        raise HTTPException(404, "lectures.not_exist")

    try:
        await service.get_note_by_user_lecture_id(session, uid, lecture_id)
        raise HTTPException(403, "note.forbidden")

    except IndexError:
        note = await service.add_note(session, uid, lecture_id, data.data, data.indexed_playtime)
        await session.commit()

    return {
        "id": note.id,
        "data": note.data,
        "indexed_playtime": note.indexed_playtime,
    }


@app.put("/api/lecture/{lecture_id}/note")
async def put_lecture_note(
        lecture_id: int, data: NewNoteRequest,
        uid: int = Depends(get_current_uid), session: AsyncSession = Depends(get_session)):

    try:
        await service.get_lecture(session, lecture_id)
    except IndexError:
        raise HTTPException(404, "lectures.not_exist")

    try:
        note = await service.get_note_by_user_lecture_id(session, uid, lecture_id)
        note = await service.update_note(session, note.id, data.data, data.indexed_playtime)
        await session.commit()

    except IndexError:
        raise HTTPException(404, "note.not_exist")

    return {
        "id": note.id,
        "data": note.data,
        "indexed_playtime": note.indexed_playtime,
    }
