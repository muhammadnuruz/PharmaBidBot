from UzTransliterator import UzTransliterator
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import unquote
from apps.orders.config import create_order, get_order_with_user, update_order, get_my_orders, get_pending_orders
from bot.buttons.text import order, my_works, free_works
from bot.dispatcher import dp, bot, Config
from bot.buttons.reply_buttons import main_menu_buttons, back_main_menu_button
from apps.telegram_users.config import get_pharmacy_staffs, get_user_by_chat_id, get_user_by_id
import aiohttp
import os

SAVE_PATH = "images/order_images/"
os.makedirs(SAVE_PATH, exist_ok=True)


@dp.message_handler(Text(equals=[order]))
async def ask_for_product_photo(msg: types.Message, state: FSMContext):
    await msg.answer("📷 Пожалуйста, отправьте фотографию продукта:", reply_markup=await back_main_menu_button())
    await state.set_state("product_photo")


@dp.message_handler(state='product_photo', content_types=ContentType.PHOTO)
async def set_product_photo(msg: types.Message, state: FSMContext):
    try:
        photo = msg.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file_info.file_path}"
        filename = f"{msg.from_user.id}_{photo.file_id}.jpg"
        local_path = os.path.join(SAVE_PATH, filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    await msg.answer("❌ Не удалось загрузить изображение из Telegram.")
                    return
                image_bytes = await resp.read()
                with open(local_path, "wb") as f:
                    f.write(image_bytes)
        from apps.telegram_users.models import TelegramUsers
        tg_user = await get_user_by_chat_id(msg.from_user.id)
        order = await create_order(
            user=tg_user,
            image=local_path,
        )
        phone_number = tg_user.phone_number
        latitude = tg_user.location_lat
        longitude = tg_user.location_lng
        location_link = f"https://www.google.com/maps?q={latitude},{longitude}" if latitude and longitude else "Неизвестно"
        accept_btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Принять заказ", callback_data=f"accept_order_{order.id}")
        )
        await msg.answer("✅ Заказ принято!", reply_markup=await main_menu_buttons(msg.from_user.id))
        staffs = await get_pharmacy_staffs()
        for staff in staffs:
            try:
                await bot.send_photo(chat_id=staff.chat_id, photo=photo.file_id,
                                     caption=f"🆕 <b>Новый заказ #{order.id}</b>\n"
                                             f"👤 <b>Пользователь:</b> {tg_user.full_name if tg_user else 'Неизвестный'}\n"
                                             f"📞 <b>Телефон:</b> {phone_number}\n"
                                             f'📍 <b>Местоположение:</b> <a href="{location_link}">Смотреть на карте</a>\n'
                                             f"📸 <b>Изображение доступно</b>", parse_mode="HTML",
                                     reply_markup=accept_btn)
            except Exception:
                continue

    except Exception as e:
        await msg.answer(f"❌ Ошибка: {e}", reply_markup=await main_menu_buttons(msg.from_user.id))
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("confirm_offer_"))
async def confirm_offer_handler(call: types.CallbackQuery):
    try:
        _, __, order_id, staff_id, price_enc, desc_enc = call.data.split("_", 5)
        order_id = int(order_id)
        staff_id = int(staff_id)
        price = unquote(price_enc)
        text = unquote(desc_enc)
        obj = UzTransliterator.UzTransliterator()
        description = obj.transliterate(text, from_="lat", to="cyr")

        await update_order(order_id=order_id, staff_id=staff_id, price=price, description=description)

        order = await get_order_with_user(order_id)
        customer = order.user
        staff = await get_user_by_chat_id(staff_id)

        staff_location = (staff.location_lat, staff.location_lng)
        user_location = (customer.location_lat, customer.location_lng)

        def loc_link(lat, lng):
            return f"https://www.google.com/maps?q={lat},{lng}" if lat and lng else "Неизвестно"

        staff_info = (
            f"👨‍🔧 <b>Вы приняли предложение!</b>\n"
            f"💰 <b>Цена:</b> {price} сум\n"
            f"📝 <b>Комментарий:</b> {description}\n"
            f"📞 <b>Телефон сотрудника:</b> {staff.phone_number or 'Неизвестно'}\n"
            f"📍 <b>Местоположение:</b> <a href='{loc_link(*staff_location)}'>Смотреть</a>"
        )
        await call.message.answer(staff_info, parse_mode="HTML")

        user_info = (
            f"📦 <b>Ваше предложение принято!</b>\n"
            f"🧑 <b>Клиент:</b> {customer.full_name}\n"
            f"📞 <b>Телефон:</b> {customer.phone_number or 'Неизвестно'}\n"
            f"📍 <b>Местоположение:</b> <a href='{loc_link(*user_location)}'>Смотреть</a>"
        )
        await bot.send_message(chat_id=staff_id, text=user_info, parse_mode="HTML")

        await call.message.delete()
        await call.answer()

    except Exception as e:
        await call.message.answer(f"❌ Ошибка при принятии предложения.\nОшибка: {e}")
        await call.answer()


@dp.message_handler(Text(my_works))
async def my_orders_handler(msg: types.Message):
    chat_id = msg.from_user.id
    orders = await get_my_orders(chat_id)
    if not orders:
        await msg.answer("📭 У вас нет заказов.")
        return
    user = await get_user_by_chat_id(chat_id)
    is_staff = user.is_staff
    await msg.answer("📋 <b>Ваши заказы:</b>", parse_mode="HTML")
    for order in orders:
        other_party = order.user if is_staff else order.staff
        other_role = "Клиент" if is_staff else "Исполнитель"
        if other_party and other_party.location_lat and other_party.location_lng:
            lat, lng = other_party.location_lat, other_party.location_lng
            location_link = f"<a href='https://www.google.com/maps?q={lat},{lng}'>📍 Смотреть на карте</a>"
        else:
            location_link = "📍 Локация: Неизвестно"
        caption = (
            f"🆔 <b>Заказ №{order.id}</b>\n"
            f"💰 <b>Цена:</b> {order.price or 'Не указано'}\n"
            f"📝 <b>Описание:</b> {order.description or 'Нет описания'}\n"
            f"👤 <b>{other_role}:</b> {other_party.full_name if other_party else '—'}\n"
            f"📞 <b>Телефон:</b> {other_party.phone_number if other_party else '—'}\n"
            f"📅 <b>Создано:</b> {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '—'}\n"
            f"{location_link}"
        )
        photo_path = os.path.join(order.image)
        try:
            with open(photo_path, "rb") as image_file:
                await msg.answer_photo(photo=image_file, caption=caption, parse_mode="HTML")
        except FileNotFoundError:
            await msg.answer("❌ Rasm fayli topilmadi.")
        except Exception as e:
            await msg.answer(f"❌ Xatolik yuz berdi:\n{e}")


@dp.message_handler(Text(free_works))
async def empty_orders_handler(msg: types.Message):
    orders = await get_pending_orders()
    if not orders:
        await msg.answer("✅ Все заказы уже были приняты.")
        return

    await msg.answer("📜 <b>Пустые заказы:</b>", parse_mode="HTML")

    for order in orders:
        user = await get_user_by_id(order.user_id) if order.user_id else None
        if user and user.location_lat and user.location_lng:
            lat, lng = user.location_lat, user.location_lng
            location_link = f"<a href='https://www.google.com/maps?q={lat},{lng}'>📍 Смотреть на карте</a>"
        else:
            location_link = "📍 Локация: Неизвестно"

        caption = (
            f"🔖 <b>Заказ №{order.id}</b>\n"
            f"💰 <b>Цена:</b> {order.price or '---'}\n"
            f"📘 <b>Описание:</b> {order.description or '---'}\n"
            f"📅 <b>Создано:</b> {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '---'}\n"
            f"👤 <b>Клиент:</b> {user.full_name if user else '---'}\n"
            f"📞 <b>Телефон:</b> {user.phone_number if user else '---'}\n"
            f"{location_link}"
        )

        photo_path = os.path.join(order.image)
        accept_button = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Принять",
                callback_data=f"accept_order_{order.id}"
            )
        )
        try:
            with open(photo_path, "rb") as image_file:
                await msg.answer_photo(photo=image_file, caption=caption, parse_mode="HTML", reply_markup=accept_button)
        except Exception as e:
            await msg.answer(f"❌ Ошибка при отправке заказа {order.id}: {e}")
