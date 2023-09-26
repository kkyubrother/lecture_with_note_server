from typing import List
from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from lecture_with_note_server.models import User
from lecture_with_note_server.models import Lecture
from lecture_with_note_server.models import Note
from lecture_with_note_server.models import NoteLog


async def get_user(session: AsyncSession, user_id: int) -> User:
    result = await session.execute(select(User).where(and_(User.id == user_id)))
    user = result.scalar()

    if not user:
        raise IndexError("users.not_exist")

    return user


async def get_user_by_email(session: AsyncSession, platform: str, email: str) -> User:
    result = await session.execute(select(User).where(and_(User.email == email, User.platform == platform)))
    user = result.scalar()

    if not user:
        raise IndexError("users.not_exist")

    return user


async def add_user(session: AsyncSession, platform: str, email: str) -> User:
    new_user = User(platform=platform, email=email)
    session.add(new_user)
    return new_user


async def get_lecture(session: AsyncSession, lecture_id: int) -> Lecture:
    result = await session.execute(select(Lecture).where(and_(Lecture.id == lecture_id)))
    lecture = result.scalar()

    if not lecture:
        raise IndexError("lectures.not_exist")

    return lecture


async def get_lecture_by_url(session: AsyncSession, url: str) -> Lecture:
    result = await session.execute(select(Lecture).where(and_(Lecture.url == url)))
    lecture = result.scalar()

    if not lecture:
        raise IndexError("lectures.not_exist")

    return lecture


async def get_lectures_by_uid(session: AsyncSession, uid: int) -> List[Lecture]:
    result = await session.execute(select(Lecture).where(and_(Lecture.user_id == uid)))
    return result.scalars().all()


async def add_lecture(session: AsyncSession, uid: int, url: str, title: str = None) -> Lecture:
    new_lecture = Lecture(user_id=uid, title=f"{title}" if title else url, url=url)
    session.add(new_lecture)
    return new_lecture


async def del_lecture(session: AsyncSession, uid: int, url: str) -> None:
    result = await session.execute(select(Lecture).where(and_(Lecture.user_id == uid, Lecture.url == url)))
    lecture = result.scalar()

    if not lecture:
        raise IndexError("lectures.not_exist")
    await session.delete(lecture)


async def get_note(session: AsyncSession, note_id: int) -> Note:
    result = await session.execute(select(Note).where(and_(Note.id == note_id)))
    note = result.scalar()

    if not note:
        raise IndexError("notes.not_exist")

    return note


async def get_note_by_user_lecture_id(session: AsyncSession, user_id: int, lecture_id: int) -> Note:
    result = await session.execute(select(Note).where(and_(Note.lecture_id == lecture_id, Note.user_id == user_id)))
    note = result.scalar()

    if not note:
        raise IndexError("notes.not_exist")

    return note


async def get_notes_by_user_id(session: AsyncSession, user_id: int) -> Note:
    result = await session.execute(select(Note).where(and_(Note.user_id == user_id)))
    note = result.scalar()

    if not note:
        raise IndexError("notes.not_exist")

    return note


async def add_note(
        session: AsyncSession,
        user_id: int, lecture_id: int, data: str, indexed_playtime: int = None) -> Note:

    result = await session.execute(select(Note).where(and_(Note.user_id == user_id, Note.lecture_id == lecture_id)))
    note = result.scalar()

    if note:
        raise IndexError("notes.exists")

    new_note = Note(user_id=user_id, lecture_id=lecture_id, data=data, indexed_playtime=indexed_playtime)
    session.add(new_note)
    return new_note


async def update_note(session: AsyncSession, note_id: int, data: str, indexed_playtime: int = None) -> Note:
    result = await session.execute(select(Note).where(and_(Note.id == note_id)))
    note = result.scalar()

    if not note:
        raise IndexError("notes.not_exist")

    new_note_log = NoteLog(note_id=note_id, data=note.data)
    session.add(new_note_log)

    note.data = data
    note.indexed_playtime = indexed_playtime
    return note
