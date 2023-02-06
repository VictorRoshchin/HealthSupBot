# Получить все записи.
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_db import bot_sqlite
from create_bot import bot
from handlers._edit_entry import cb_entry
from keyboards.client import kb_client_start


async def print_entry(user_id, count=None):
    entries = await bot_sqlite.sql_get_all_command(user_id, count)

    for e in entries:
        await bot.send_message(user_id, f'Дата: {".".join(reversed(e[4].split("-")))}, время: {e[5][:5]}\n'
                                        f'Вехнее давление: {e[0]}\n'
                                        f'Нижнее давление: {e[1]}\n'
                                        f'Пульс: {e[2]}\n'
                                        f'Комментарий: {e[3]}')


async def print_and_edit_entry(user_id, count=None):
    entries = await bot_sqlite.sql_get_all_command(user_id, count)

    for e in entries:
        await bot.send_message(user_id, f'Дата: {".".join(reversed(e[4].split("-")))}, время: {e[5][:5]}\n'
                                        f'Вехнее давление: {e[0]}\n'
                                        f'Нижнее давление: {e[1]}\n'
                                        f'Пульс: {e[2]}\n'
                                        f'Комментарий: {e[3]}',
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(text='Изменить', callback_data=cb_entry.new(
                                       action='edit_entry',
                                       entry_id=e[-1],
                                       top_pressure=e[0],
                                       lower_pressure=e[1],
                                       pulse=e[2]
                                   )),
                                   InlineKeyboardButton(text='Удалить', callback_data=f'del {e[-1]} {user_id}')
                               ))


async def get_entries(message: types.Message):
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Одна запись', callback_data='get_last'),
        InlineKeyboardButton(text='Десять записей', callback_data='get_ten')
    )
    await message.reply('Сколько записей выгрузить?', reply_markup=kb)


async def get_and_edit_entries(message: types.Message):

    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Одна запись', callback_data='edit_last'),
        InlineKeyboardButton(text='Десять записей', callback_data='edit_ten')
    )
    await message.reply('Сколько записей выгрузить?', reply_markup=kb)


async def get_entry_last(call: types.CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    await print_entry(user_id, count=1)
    await bot.send_message(user_id, 'Выгружена последняя запись', reply_markup=kb_client_start)


async def edit_entry_last(call: types.CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    await print_and_edit_entry(user_id, count=1)
    await bot.send_message(user_id, 'Выгружена последняя запись', reply_markup=kb_client_start)


async def get_entry_ten(call: types.CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    await print_entry(user_id, count=10)
    await bot.send_message(user_id, 'Выгружены последние 10 записей', reply_markup=kb_client_start)


async def edit_entry_ten(call: types.CallbackQuery):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    await print_and_edit_entry(user_id, count=10)
    await bot.send_message(user_id, 'Выгружены последние 10 записей', reply_markup=kb_client_start)


def register_handlers_getter(disp: Dispatcher):
    # Входная команда и генерация callbacks
    disp.register_message_handler(get_entries, Text(equals='Выгрузить', ignore_case=True))

    disp.register_message_handler(get_and_edit_entries, Text(equals='Редактировать', ignore_case=True))

    # Вывод последней записи.
    disp.register_callback_query_handler(edit_entry_last, lambda x: x.data.startswith('edit_last'))
    # Вывод последних 10 записей.
    disp.register_callback_query_handler(edit_entry_ten, lambda x: x.data.startswith('edit_ten'))


    # Вывод последней записи.
    disp.register_callback_query_handler(get_entry_last, lambda x: x.data.startswith('get_last'))
    # Вывод последних 10 записей.
    disp.register_callback_query_handler(get_entry_ten, lambda x: x.data.startswith('get_ten'))
