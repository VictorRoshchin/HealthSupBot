from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_db import bot_sqlite
from create_bot import bot


async def delete_command(message: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Последняя запись', callback_data='delete_last'),
        InlineKeyboardButton(text='Вывести 10 последних', callback_data='get_ten')
    )
    await message.reply('Выберите запись для удаления',
                        reply_markup=kb)


# # Удалить запись (создание callback).
# async def del_entry(message: types.Message):
#     read = await bot_sqlite.sql_get_all_command(message)
#     for ret in read:
#         await bot.send_message(message.from_user.id,
#                                f'Удалить запись №{ret[-1]} от {ret[3]}\nПоказания: {ret[0]}/{ret[1]}-{ret[2]}?',
#                                reply_markup=InlineKeyboardMarkup().add(
#                                    InlineKeyboardButton(
#                                        f'Удалить', callback_data=f'del {ret[-1]} {message.from_user.id}'
#                                    ))
#                                )


# Удаление записи (обработка callback).
async def del_callback(call: types.CallbackQuery):
    print(call.data)
    entry_id, table = call.data.replace('del ', '').split()
    await bot_sqlite.sql_del_command(entry_id, table)
    await call.answer(text=f'Запись запись №{entry_id} удалена')


def register_deleter(disp: Dispatcher):
    # disp.register_message_handler(del_entry, Text(equals='Удалить', ignore_case=True))
    disp.register_callback_query_handler(del_callback, lambda x: x.data and x.data.startswith('del '))
