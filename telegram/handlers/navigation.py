from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from telegram.states.states import AppealStates
from telegram.keyboards.keyboards import main_menu_kb, category_kb, appeal_type_kb, write_appeal_kb

async def go_to_main_menu(message: Message, state: FSMContext):
    await state.set_state(AppealStates.MAIN_MENU)
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

async def go_to_choose_type(message: Message, state: FSMContext):
    await state.set_state(AppealStates.CHOOSE_APPEAL_TYPE)
    await message.answer("Выберите тип обращения:", reply_markup=appeal_type_kb())

async def go_to_choose_category(message: Message, state: FSMContext):
    await state.set_state(AppealStates.CHOOSE_CATEGORY)
    await message.answer("Выберите категорию обращения:", reply_markup=category_kb())

async def go_to_write_appeal(message: Message, state: FSMContext):
    await state.set_state(AppealStates.WRITE_APPEAL)
    await message.answer("Пожалуйста, опишите вашу проблему:", reply_markup=write_appeal_kb())



