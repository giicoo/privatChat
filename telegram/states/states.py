from aiogram.fsm.state import StatesGroup, State

class AppealStates(StatesGroup):
    MAIN_MENU = State()
    CHOOSE_APPEAL_TYPE = State()
    CHOOSE_CATEGORY = State()
    WRITE_APPEAL = State()
