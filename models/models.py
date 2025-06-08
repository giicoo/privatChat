from sqlalchemy import DateTime, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
from sqlalchemy.types import BigInteger

class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Fix for large Telegram IDs
    tg_name: Mapped[str] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(64), nullable=True)
    trust: Mapped[int] = mapped_column(Integer, default=0)

class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tg_message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    answer_by: Mapped[int] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class MediaModel(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int] 
    tg_media_group_id: Mapped[int]
    tg_media_id: Mapped[int]
