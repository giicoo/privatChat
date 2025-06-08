from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import RULES_TEXT
from environment import DB_URL
from aiogram import Bot, F
from environment import ADMIN_CHAT_ID
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from telegram.handlers.middleware import block_user
from aiogram.fsm.state import default_state
from aiogram.filters import StateFilter
from telegram.states.states import AppealStates
from telegram.keyboards.keyboards import back_to_main_kb
from telegram.senders.admin import forward_to_admins
from telegram.handlers.navigation import go_to_main_menu, go_to_choose_type, go_to_choose_category, go_to_write_appeal
from repository.repository import Repository
from models.models import UserModel, MessageModel
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

repo = Repository(async_session_maker)

router = Router()


# скипаем все сообщения которые в группу админов приходят
@router.message(F.chat.type.in_({"group", "supergroup"}) & ~F.reply_to_message)
async def handle_message_not_reply(message: Message):
    #await message.answer(text="да", reply_markup=ReplyKeyboardRemove())
    pass

@router.message((F.text == "/start") & ~F.chat.type.in_({"group", "supergroup"}))
async def start_handler(message: Message, state: FSMContext):
    await repo.create_user(UserModel(tg_id=message.from_user.id,
                                     tg_name=message.from_user.full_name,
                                     trust=0,
                                    ))
    await state.update_data(tg_id=message.from_user.id, anonymous=False)
    await go_to_main_menu(message, state)

@router.message((F.text == "📜 Правила обращений") & ~F.chat.type.in_({"group", "supergroup"}))
async def rules_handler(message: Message):
    await message.answer(RULES_TEXT)

@router.message((F.text == "✉️ Оставить обращение") & ~F.chat.type.in_({"group", "supergroup"}))
async def appeal_type_handler(message: Message, state: FSMContext):
    await state.update_data(tg_id=message.from_user.id)
    await go_to_choose_type(message, state)

@router.message((F.text == "⬅️ В главное меню") & ~F.chat.type.in_({"group", "supergroup"}))
async def appeal_type_handler(message: Message, state: FSMContext):
    await go_to_main_menu(message, state)




@router.message(AppealStates.CHOOSE_APPEAL_TYPE, F.text.in_(["🔒 Анонимно", "📞 С обратной связью"]))
async def category_handler(message: Message, state: FSMContext):
    is_anon = message.text == "🔒 Анонимно"
    await state.update_data(appeal_type=message.text, anonymous=is_anon)
    await go_to_choose_category(message, state)

@router.message(AppealStates.CHOOSE_APPEAL_TYPE, F.text == "⬅️ Назад")
async def back_to_main_from_type(message: Message, state: FSMContext):
    await go_to_main_menu(message, state)




@router.message(AppealStates.CHOOSE_CATEGORY, F.text.in_(["🚨 Криминал", "🏘️ Социальная проблема", "📌 Прочее"]))
async def write_appeal_handler(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await go_to_write_appeal(message, state)

@router.message(AppealStates.CHOOSE_CATEGORY, F.text == "⬅️ Назад")
async def back_to_type_from_category(message: Message, state: FSMContext):
    await go_to_choose_type(message, state)



# обрабатываем вначале, чтоб не путалось с сообщением
@router.message(AppealStates.WRITE_APPEAL, F.text == "⬅️ Назад")
async def back_to_category_from_write(message: Message, state: FSMContext):
    await go_to_choose_category(message, state)

@router.message(AppealStates.WRITE_APPEAL)
async def submit_appeal_handler(message: Message, state: FSMContext, bot: Bot):     
    message_text = message.text or message.caption
    user_data = await state.get_data()
    if (message.text or message.caption):
        message_db_id = await repo.create_message(MessageModel(tg_user_id=message.from_user.id, 
                                           tg_message_id=message.message_id,
                                           category=user_data["category"],
                                           text=message_text))
        user_data = await state.update_data(message_db_id=message_db_id)
    
    color = None
    if not user_data["anonymous"]:
        user = await repo.get_user_by_id(message.from_user.id)
        if user.trust < 5:
            color = "🟢"
        elif user.trust >= 5 and user.trust < 10:
            color = "🟡"
        else:
            color = "🔴"
    

    if await forward_to_admins(bot, message, user_data, color):
        if not (message.text or message.caption):
        # Игнорируем если нет текста или подписи (потому что если альбом то фотки отдельно сюда прилетают)
            return
        await message.reply(f"✅ Обращение #{message_db_id} принято!", reply_markup=back_to_main_kb())
        await go_to_main_menu(message, state)






@router.message(F.reply_to_message & F.chat.type.in_({"group", "supergroup"}))
async def admin_reply_handler(message: Message, bot: Bot):
    try:
        original_text = message.reply_to_message.text or message.reply_to_message.caption
        
        if 'UserID:' not in original_text:
            await message.answer("⚠️ Это анонимное обращение, ответ невозможен")
            return

        if '#' not in original_text:
            return  # не обращение

        message_db_id = int(original_text.split('#')[1].split()[0])
        msg = await repo.get_message_by_id(message_db_id)
        admin_msg_id = await repo.create_message(MessageModel(tg_user_id=message.from_user.id, 
                                           tg_message_id=message.message_id,
                                           category="ADMIN ANSWER",
                                           answer_by=msg.id,
                                           text=message.text))
        reply_text = f"✉️ Ответ поддержки на обращение #{message_db_id}:\n{message.text}"

     
        await bot.send_message(
            chat_id=msg.tg_user_id,
            text=reply_text,
            reply_to_message_id=msg.tg_message_id
        )

    except Exception as e:
        from telegram.utils.utils import logger
        logger.error(f"Ошибка обработки ответа админа: {e}")




@router.callback_query(F.data.startswith("action:"))
async def handle_action(callback_query: CallbackQuery, bot: Bot):
    callback = callback_query.data.split(":")
    action = callback[1]
    messages_id = [int(i) for i in callback[3:]]
    user_id = int(callback[2])
    if action == "block":
        block_user.append(user_id)
        for i in messages_id:
            await bot.delete_message(chat_id=ADMIN_CHAT_ID, message_id=i)
        await bot.delete_message(chat_id=ADMIN_CHAT_ID, message_id=callback_query.message.message_id)

    elif action == "skip":
        for i in messages_id:
            await bot.delete_message(chat_id=ADMIN_CHAT_ID, message_id=i)
        await bot.delete_message(chat_id=ADMIN_CHAT_ID, message_id=callback_query.message.message_id)

    
    await callback_query.answer()  # чтобы убрать «часики»




@router.message(StateFilter(default_state))
async def default(message: Message, state:FSMContext):
    await go_to_main_menu(message, state)