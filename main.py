from aiogram.utils import executor

from bot_db import bot_sqlite
from create_bot import dp
from handlers import client


async def on_startup(_):
    print('Бот вышел в онлайн')
    bot_sqlite.sql_start()


client.register_handlers_client(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
