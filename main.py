from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError
import asyncio
from environment import BOT_TOKEN
from telegram.handlers.handlers import router, engine
from models.models import Base
from telegram.handlers.middleware import LoggingMiddleware


async def main():
    try:
        bot = Bot(token=BOT_TOKEN)
    except TokenValidationError:
        print("❌ Invalid bot token in config.py")
        return
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.message.middleware(LoggingMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())