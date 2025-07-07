import logging
from aiogram import executor
from bot.dispatcher import dp
import bot.handlers

admins = [1974800905, 999090234]

logging.basicConfig(level=logging.WARNING)

logging.getLogger('aiogram').setLevel(logging.ERROR)
logging.getLogger('aiohttp').setLevel(logging.ERROR)


async def on_startup(dispatcher):
    print("✅ Bot ishga tushdi!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
