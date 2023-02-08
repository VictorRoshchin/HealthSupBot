from aiogram.utils import executor

from db_api.api_requests import db_start
from create_bot import dp
from handlers import register


async def on_startup(_):
    print('Бот вышел в онлайн')
    db_start()


register.register_handlers(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
