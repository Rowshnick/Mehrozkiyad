from aiogram.fsm.state import State, StatesGroup


class NatalStates(StatesGroup):
    ASK_NAME = State()
    ASK_DATE = State()
    ASK_TIME = State()
    ASK_CITY = State()
