from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterState(StatesGroup):
    phone_number = State()
    location = State()
    photo = State()
    done = State()


class OrderUpdateState(StatesGroup):
    enter_price = State()
    enter_description = State()
