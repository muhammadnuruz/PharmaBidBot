import asyncio
import json
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType
from aiogram.utils.exceptions import ChatNotFound, BotBlocked, RetryAfter, MessageNotModified

from apps.telegram_users.config import get_telegram_users
from bot.buttons.reply_buttons import (
    main_menu_buttons, back_main_menu_button,
    advert_menu_buttons, admin_menu_buttons
)
from bot.buttons.text import adverts, none_advert, forward_advert
from bot.dispatcher import dp, bot
from main import admins


@dp.message_handler(commands='admin')
async def admin_handler(msg: types.Message):
    if msg.from_user.id in admins:
        await msg.answer("Добро пожаловать в админ-меню ℹ️", reply_markup=await admin_menu_buttons())
    else:
        await msg.answer("У вас нет прав администратора ❌")


@dp.message_handler(Text(adverts))
async def advert_handler(msg: types.Message):
    if msg.from_user.id in admins:
        await msg.answer("В каком формате отправить сообщение ❓", reply_markup=await advert_menu_buttons())
    else:
        await msg.answer("Эта функция доступна только администраторам ❌")


@dp.message_handler(Text(none_advert))
async def none_advert_handler(msg: types.Message, state: FSMContext):
    if msg.from_user.id in admins:
        await state.set_state("advert")
        await msg.answer("Отправьте сообщение ❗", reply_markup=await back_main_menu_button())


@dp.message_handler(state='advert', content_types=ContentType.ANY)
async def send_advert_to_users(msg: types.Message, state: FSMContext):
    await state.finish()
    users = await get_telegram_users()
    success_count = 0
    failed_count = 0
    session = await msg.answer(text="✅ Началась отправка сообщений!")

    for user in users:
        try:
            await msg.copy_to(chat_id=int(user.chat_id), caption=msg.caption,
                              caption_entities=msg.caption_entities, reply_markup=msg.reply_markup)
            success_count += 1
            await asyncio.sleep(0.05)
        except (ChatNotFound, BotBlocked):
            failed_count += 1
        except RetryAfter as e:
            await asyncio.sleep(e.timeout)
        except Exception as e:
            failed_count += 1
            continue

    await session.delete()
    await msg.answer(
        text=f"Рассылка завершена ✅\n\n"
             f"✅ Доставлено {success_count} пользователям\n"
             f"❌ Не доставлено {failed_count} пользователям",
        reply_markup=await main_menu_buttons(msg.from_user.id)
    )


@dp.message_handler(Text(forward_advert))
async def forward_advert_handler(msg: types.Message, state: FSMContext):
    if msg.from_user.id in admins:
        await state.set_state('send_forward')
        await msg.answer("📨 Отправьте пересылаемое сообщение", reply_markup=await back_main_menu_button())


@dp.message_handler(state='send_forward', content_types=ContentType.ANY)
async def send_forward_to_users(msg: types.Message, state: FSMContext):
    await state.finish()
    users = await get_telegram_users()
    success_count, failed_count = 0, 0
    session_msg = await msg.answer(text="✅ Началась рассылка пересылаемых сообщений!")

    for user in users:
        try:
            await bot.forward_message(chat_id=int(user.chat_id), from_chat_id=msg.chat.id, message_id=msg.message_id)
            success_count += 1
            await asyncio.sleep(0.05)
        except (ChatNotFound, BotBlocked):
            failed_count += 1
        except RetryAfter as e:
            await asyncio.sleep(e.timeout)
        except Exception:
            failed_count += 1
            continue

    await session_msg.delete()
    await msg.answer(
        text=f"📢 Рассылка пересылаемых сообщений завершена!\n\n"
             f"✅ Доставлено {success_count} пользователям\n"
             f"❌ Не доставлено {failed_count} пользователям",
        reply_markup=await main_menu_buttons(msg.from_user.id)
    )