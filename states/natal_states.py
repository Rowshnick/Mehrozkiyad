from states.natal_states import NatalStates

class NatalStates(StatesGroup):
    ASK_NAME = State()
    ASK_DATE = State()
    ASK_TIME = State()
    ASK_CITY = State()
