from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.buttons.reply_buttons import main_menu_buttons
from bot.buttons.text import back_main_menu, change_location
from bot.dispatcher import dp
from bot.states import RegisterState
from apps.telegram_users.config import (
    get_user_by_chat_id,
    create_user_by_chat_id,
    update_user_by_chat_id
)


@dp.message_handler(Text(equals=[back_main_menu]), state='*')
async def back_main_menu_msg(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("🔙 Главное меню", reply_markup=await main_menu_buttons(msg.from_user.id))


@dp.callback_query_handler(Text(equals=[back_main_menu]), state='*')
async def back_main_menu_cb(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer("🔙 Главное меню", reply_markup=await main_menu_buttons(call.from_user.id))


@dp.message_handler(CommandStart())
async def start_register(msg: types.Message, state: FSMContext):
    user = await get_user_by_chat_id(msg.from_user.id)
    if user:
        await msg.answer("♻ Бот обновлен", reply_markup=await main_menu_buttons(msg.from_user.id))
    else:
        await state.finish()
        await msg.answer(
            "📱 Пожалуйста, отправьте свой номер телефона:",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                KeyboardButton("📱 Отправить номер телефона", request_contact=True)
            )
        )
        await RegisterState.phone_number.set()


@dp.message_handler(content_types=types.ContentType.CONTACT, state=RegisterState.phone_number)
async def get_phone(msg: types.Message, state: FSMContext):
    await state.update_data(phone_number=msg.contact.phone_number)
    await msg.answer(
        "📍 Отправьте свое местоположение:",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            KeyboardButton("📍 Отправить местоположение", request_location=True)
        )
    )
    await RegisterState.location.set()


@dp.message_handler(content_types=types.ContentType.LOCATION, state=RegisterState.location)
async def get_location(msg: types.Message, state: FSMContext):
    await state.update_data(
        location_lat=msg.location.latitude,
        location_lng=msg.location.longitude
    )
    await complete_register(msg, state)


async def complete_register(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await create_user_by_chat_id(
        chat_id=msg.from_user.id,
        full_name=msg.from_user.full_name,
        phone_number=data.get("phone_number"),
        username=msg.from_user.username,
        location_lat=data.get("location_lat"),
        location_lng=data.get("location_lng"),
    )
    if user:
        await msg.answer("✅ Вы успешно зарегистрировались!", reply_markup=await main_menu_buttons(msg.from_user.id))
    else:
        await msg.answer("❗ Произошла ошибка при создании пользователя.")
    await state.finish()


@dp.message_handler(text=change_location)
async def start_location_change(msg: types.Message):
    await msg.answer(
        "📍 Пожалуйста, отправьте новую локацию:",
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            KeyboardButton("📍 Отправить местоположение", request_location=True)
        )
    )


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def update_location(msg: types.Message):
    updated_user = await update_user_by_chat_id(
        chat_id=msg.from_user.id,
        full_name=msg.from_user.full_name,
        username=msg.from_user.username,
        location_lat=msg.location.latitude,
        location_lng=msg.location.longitude,
    )
    if updated_user:
        await msg.answer("✅ Ваша локация успешно обновлена!",
                         reply_markup=await main_menu_buttons(msg.from_user.id))
    else:
        await msg.answer("❗ Произошла ошибка при обновлении локации.",
                         reply_markup=await main_menu_buttons(msg.from_user.id))
