from aiogram.types import ReplyKeyboardMarkup

from apps.telegram_users.config import get_user_by_chat_id
from bot.buttons.text import adverts, none_advert, forward_advert, order, free_works, back_main_menu, \
    change_location, my_works


async def main_menu_buttons(chat_id: int):
    user = await get_user_by_chat_id(chat_id)
    if user.is_staff is True:
        design = [
            [free_works],
            [my_works]
        ]
    else:
        design = [
            [order],
            [my_works],
            [change_location]
        ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def back_main_menu_button():
    design = [[back_main_menu]]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def admin_menu_buttons():
    design = [
        [adverts],
        [back_main_menu]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def advert_menu_buttons():
    design = [
        [none_advert, forward_advert],
        [back_main_menu]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
