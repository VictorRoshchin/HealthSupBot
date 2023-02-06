from aiogram import types

from create_bot import bot
from handlers._email import FSMEmail


# Старт
async def command_start(message: types.Message):
    await FSMEmail.email.set()
    await bot.send_message(message.from_user.id, '''
    Бот разработан для ведения дневника давления
    Поддерживаемый функционал:
    /Запись - создание записи в журнале и сохранение в базе данных
    /Выгрузить - выгрузка записей из базы данных
    /Удалить - удалить запись из базы данных
    /Изменить - изменить запись
    /Отчет - составить отчет и отправить на электронную почту

    Для начала мне нужно, чтобы вы сообщили мне электронную почту, на которую будут высылаться отчеты
    ''')
