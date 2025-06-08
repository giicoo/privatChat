from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

# TODO: неправильно
block_user = []

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        if event.from_user.id in block_user: return
        print(f"[LOG] User {event.from_user.id} sent: {event.text}")
        return await handler(event, data)
