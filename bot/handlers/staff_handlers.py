from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram import types

from apps.orders.config import get_order_with_user
from apps.telegram_users.config import get_user_by_chat_id
from bot.buttons.reply_buttons import main_menu_buttons, back_main_menu_button
from bot.dispatcher import dp, bot
from urllib.parse import quote
from bot.states import OrderUpdateState


@dp.callback_query_handler(lambda c: c.data.startswith("accept_order_"))
async def accept_order_handler(call: CallbackQuery, state: FSMContext):
    order_id = call.data.split("_")[-1]
    await state.update_data(order_id=order_id)
    await call.message.delete()
    await call.message.answer("💰 Введите цену заказа:", reply_markup=await back_main_menu_button())
    await OrderUpdateState.enter_price.set()
    await call.answer()


@dp.message_handler(state=OrderUpdateState.enter_price, content_types=types.ContentType.TEXT)
async def process_price(msg: types.Message, state: FSMContext):
    await state.update_data(price=msg.text)
    await msg.answer("📝 Пожалуйста, введите комментарий к заказу:")
    await OrderUpdateState.enter_description.set()


@dp.callback_query_handler(lambda c: c.data.startswith("accept_order_"))
async def accept_order_handler(call: CallbackQuery, state: FSMContext):
    order_id = call.data.split("_")[-1]
    await state.update_data(order_id=order_id)
    await call.message.delete()
    await call.message.answer("💰 Введите цену заказа:", reply_markup=await back_main_menu_button())
    await OrderUpdateState.enter_price.set()
    await call.answer()


@dp.message_handler(state=OrderUpdateState.enter_price, content_types=types.ContentType.TEXT)
async def process_price(msg: types.Message, state: FSMContext):
    await state.update_data(price=msg.text)
    await msg.answer("📝 Пожалуйста, введите комментарий к заказу:")
    await OrderUpdateState.enter_description.set()


@dp.message_handler(state=OrderUpdateState.enter_description, content_types=types.ContentType.TEXT)
async def process_description(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    staff_id = msg.from_user.id
    description = msg.text
    price = data['price']
    order_id = int(data['order_id'])
    await msg.answer("📨 Ваше предложение отправлено клиенту!",
                     reply_markup=await main_menu_buttons(msg.from_user.id))
    order = await get_order_with_user(order_id)
    tg_user = await get_user_by_chat_id(msg.from_user.id)
    user_chat_id = order.user.chat_id
    phone_number = tg_user.phone_number
    latitude = tg_user.location_lat
    longitude = tg_user.location_lng
    location_link = f"https://www.google.com/maps?q={latitude},{longitude}" if latitude and longitude else "Неизвестно"

    offer_summary = (
        f"📦 <b>Новая заявка по заказу #{order.id}</b>\n"
        f"👨‍🔧 <b>От сотрудника: {msg.from_user.full_name or 'Сотрудник'}</b>\n"
        f"💰 <b>Цена: {price} сум</b>\n"
        f"📝 <b>Комментарий: {description}</b>\n"
        f"📞 <b>Телефон:</b> {phone_number}\n"
        f'📍 <b>Местоположение:</b> <a href="{location_link}">Смотреть на карте</a>\n'
    )

    cb_data = f"confirm_offer_{order_id}_{staff_id}_{quote(price, safe='')}_{quote(description, safe='')}"

    accept_offer_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text="✅ Принять предложение",
            callback_data=cb_data
        )
    )

    try:
        await bot.send_message(
            chat_id=user_chat_id,
            text=offer_summary,
            reply_markup=accept_offer_button,
            parse_mode="HTML"
        )
    except Exception as e:
        await msg.answer(f"❌ Не удалось отправить сообщение клиенту.\nОшибка: {e}")

    await state.finish()
