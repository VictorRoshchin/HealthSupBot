from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from db_api import api_requests
from create_bot import bot


# Удаление записи (обработка callback).
async def del_callback(call: types.CallbackQuery):

    entry_id = call.data.replace('delete_entry ', '')
    entry_check = await api_requests.get(call.from_user.id, entry_check=entry_id)
    if entry_check:
        await api_requests.delete(call.from_user.id, entry_id=entry_id)
        await call.answer(text=f'Запись запись №{entry_id} удалена')

    else:
        await call.answer(text=f'Такой записи не существует')


def register_delete(disp: Dispatcher):

    disp.register_callback_query_handler(del_callback, lambda x: x.data and x.data.startswith('delete_entry'))
