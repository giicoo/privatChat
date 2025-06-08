from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import Base, UserModel, MessageModel
from sqlalchemy.ext.asyncio import create_async_engine
from environment import DB_URL

class Repository:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def create_user(self, user: UserModel):
        async with self.session_maker() as session:
            async with session.begin():
                session.add(user)
            # тут коммит происходит автоматически

    async def create_message(self, msg: MessageModel) -> int:
        async with self.session_maker() as session:
            async with session.begin():
                session.add(msg)
            await session.refresh(msg)
            return msg.id

    async def get_message_by_id(self, id: int) -> MessageModel:
        async with self.session_maker() as session:
            result = await session.execute(select(MessageModel).filter_by(id=id))
            return result.scalar_one_or_none()
        
    async def get_user_by_id(self, tg_id: int) -> UserModel:
        async with self.session_maker() as session:
            result = await session.execute(select(UserModel).filter_by(tg_id=tg_id))
            return result.scalar_one_or_none()


