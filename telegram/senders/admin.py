import asyncio
from aiogram.types import InputMediaPhoto
from aiogram import Bot
from environment import ADMIN_CHAT_ID
from telegram.keyboards.keyboards import admin_kb
from telegram.utils.utils import logger

# Глобальный буфер для альбомов
media_groups_buffer = {}  # group_id: {"photos": [], "user_data": ..., "message_id": ..., "timer_task": ...}

async def schedule_album_send(bot, group_id):
    await asyncio.sleep(3)  # ждем 3 секунды
    album_data = media_groups_buffer.get(group_id)
    if album_data:
        await _send_album(bot, album_data)

        # Очистить буфер
        del media_groups_buffer[group_id]

async def forward_to_admins(bot: Bot, message, user_data, color):
    
    try:
        if message.media_group_id:
            group_id = message.media_group_id

            if group_id not in media_groups_buffer:
                media_groups_buffer[group_id] = {
                    "photos": [],
                    "user_data": user_data,
                    "text": message.text,
                    "timer_task": None
                }
            if user_data:
                media_groups_buffer[group_id]["user_data"]=user_data
            if message.caption:
                media_groups_buffer[group_id]["text"]=message.caption

            media_groups_buffer[group_id]["photos"].append(message)

            # Запускаем таймер, если ещё не запущен
            if media_groups_buffer[group_id]["timer_task"] is None:
                media_groups_buffer[group_id]["timer_task"] = asyncio.create_task(schedule_album_send(bot, group_id, color))

            return True

        # Если обычное сообщение с фото (одиночное)
        if message.photo:
            await _send_photo(bot, message, user_data, color)
            return True

        # Просто текст
        if message.text:
            await _send_text(bot, message, user_data, color)
            return True

    except Exception as e:
        logger.error(f"Ошибка пересылки админам: {e}")
        return False

async def _send_album(bot: Bot, album_data, color):
    try:
        tg_id = album_data["user_data"]['tg_id']
        category = album_data["user_data"]['category']
        anonymous = album_data["user_data"]['anonymous']
        message_db_id = album_data["user_data"]['message_db_id']
        media = []
        photos = album_data["photos"]
        text = album_data["text"]

        trust_color = color or "⚫"
        msg_text = f"#{message_db_id} {trust_color} Категория: {category}\n{text}"
        

        if anonymous:
            msg_text = f"🕶️ АНОНИМНО\n{msg_text}"
        else:
            msg_text = f"👤 UserID: {tg_id}\n{msg_text}"

        if photos[0].caption:
            msg_text += photos[0].caption

        for i, msg in enumerate(photos):
            photo = msg.photo[-1]
            if i == 0:
                media.append(InputMediaPhoto(media=photo.file_id, caption=msg_text))
            else:
                media.append(InputMediaPhoto(media=photo.file_id))
        sent_messages = await bot.send_media_group(chat_id=ADMIN_CHAT_ID, media=media)
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📎 Обращение #{message_db_id} — выберите действие:",
            reply_markup=admin_kb([str(i.message_id) for i in sent_messages], tg_id)
        )
    except Exception as e:
        logger.error(f"_send_album: {e}")

async def _send_photo(bot: Bot, message, user_data, color):
    tg_id = user_data['tg_id']
    category = user_data['category']
    anonymous = user_data['anonymous']
    message_db_id = user_data['message_db_id']
    caption = message.caption or ""
    
    trust_color = color or "⚫"
    msg_text = f"#{message_db_id} {trust_color} Категория: {category}\n{caption}"

    if anonymous:
        msg_text = f"🕶️ АНОНИМНО\n{msg_text}"
    else:
        msg_text = f"👤 UserID: {tg_id}\n{msg_text}"

    sent_message = await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=message.photo[-1].file_id, caption=msg_text)
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📎 Обращение #{message_db_id} — выберите действие:",
        reply_markup=admin_kb([sent_message.message_id], tg_id)
    )
    return True

async def _send_text(bot: Bot, message, user_data, color):
    tg_id = user_data['tg_id']
    category = user_data['category']
    anonymous = user_data['anonymous']
    message_db_id = user_data['message_db_id']
    trust_color =  color or "⚫"

    msg_text = f"#{message_db_id} {trust_color} Категория: {category}\n{message.text}"

    if anonymous:
        msg_text = f"🕶️ АНОНИМНО\n{msg_text}"
    else:
        msg_text = f"👤 UserID: {tg_id}\n{msg_text}"

    sent_message = await bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg_text)
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📎 Обращение #{message_db_id} — выберите действие:",
        reply_markup=admin_kb([sent_message.message_id], tg_id)
    )

    return True


