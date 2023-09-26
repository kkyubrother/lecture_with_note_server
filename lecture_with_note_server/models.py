import datetime

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship, backref

from lecture_with_note_server.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(32))
    email = Column(String(256))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    title = Column(String(256))
    url = Column(String(1024))

    __table_args__ = (UniqueConstraint("user_id", "url"), )


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lecture_id = Column(Integer, ForeignKey("lectures.id", ondelete='CASCADE'))
    data = Column(Text)
    indexed_playtime = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, default=None)
    lecture = relationship('Lecture', backref=backref('lectures', cascade='delete'))


class NoteLog(Base):
    __tablename__ = "note_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey("note_logs.id"))
    data = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
