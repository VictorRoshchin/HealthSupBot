from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from bot_db import bot_sqlite
from create_bot import bot
from keyboards.client import kb_client_start, kb_client_cancel

# Состояние для callback.
cb_entry = CallbackData('edit_entry', 'action', 'entry_id', 'top_pressure', 'lower_pressure', 'pulse')


# Состояние изменения записи.
class FSMChange(StatesGroup):
    entries = State()


# Вывод записей с кнопкой для изменения.
async def change_item(message: types.Message):
    read = await bot_sqlite.sql_get_all_command(message)
    for ret in read:
        await bot.send_message(message.from_user.id,
                               f'Изменить запись №{ret[-1]} от {ret[3]}\nПоказания: {ret[0]}/{ret[1]}-{ret[2]}?',
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(
                                       text='Изменить',
                                       callback_data='edit ')
                                   )
                               )


# Для временного хранения id.
entry_change = None


# Изменение записи (создание callback).
async def print_update_entry(user_id, entry_id, top_pressure, lower_pressure, pulse):
    txt = f"""Новые значения верхнего, нижнего давлений и пульса: {top_pressure}/{lower_pressure}-{pulse}"""
    await bot.send_message(user_id, txt, reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='Подтвердить', callback_data=cb_entry.new(
                                   action='edit_finish',
                                   entry_id=entry_id,
                                   top_pressure=top_pressure,
                                   lower_pressure=lower_pressure,
                                   pulse=pulse
                               )),
        InlineKeyboardButton(text='Изменить', callback_data=cb_entry.new(
                                   action='edit_entry',
                                   entry_id=entry_id,
                                   top_pressure=top_pressure,
                                   lower_pressure=lower_pressure,
                                   pulse=pulse
                               )),
    ))


class FSMHealthEdit(StatesGroup):
    top = State()
    lower = State()
    pulse = State()


async def edit_entry(call: types.CallbackQuery, callback_data: dict):
    global entry_id
    entry_id = callback_data['entry_id']
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    await FSMHealthEdit.top.set()
    await bot.send_message(user_id, 'Введите значение верхнего давления', reply_markup=kb_client_cancel)


async def edit_top_pressure_state(message: types.Message, state: FSMContext):
    # await message.delete()
    async with state.proxy() as data:
        data['top'] = message.text
    await FSMHealthEdit.next()
    await bot.send_message(message.from_user.id, 'Напишите нижнее давление', reply_markup=kb_client_cancel)


async def edit_lower_pressure_state(message: types.Message, state: FSMContext):
    # await message.delete()
    async with state.proxy() as data:
        data['lower'] = message.text
    await FSMHealthEdit.next()
    await bot.send_message(message.from_user.id, 'Напишите пульс', reply_markup=kb_client_cancel)


async def edit_pulse_state(message: types.Message, state: FSMContext):
    global entry_id
    user_id = message.from_user.id
    # await message.delete()
    async with state.proxy() as data:
        data['pulse'] = message.text
        top = data['top']
        lower = data['lower']
        pulse = data['pulse']
    await state.finish()
    await print_update_entry(user_id, entry_id, top, lower, pulse)


async def edit_finish(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    user_id = callback_data['user_id']
    entry_id = callback_data['entry_id']
    top_pressure = callback_data['top_pressure']
    lower_pressure = callback_data['lower_pressure']
    pulse = callback_data['pulse']
    await bot_sqlite.sql_update_command(user_id, entry_id, top_pressure, lower_pressure, pulse)
    await bot.send_message(user_id, 'Запись изменена', reply_markup=kb_client_start)


def register_editor(disp: Dispatcher):
    disp.register_callback_query_handler(edit_entry, cb_entry.filter(action=['edit_entry', 'edit_top_pressure']))
    disp.register_message_handler(edit_top_pressure_state, state=FSMHealthEdit.top)
    disp.register_message_handler(edit_lower_pressure_state, state=FSMHealthEdit.lower)
    disp.register_message_handler(edit_pulse_state, state=FSMHealthEdit.pulse)
    disp.register_callback_query_handler(edit_finish, cb_entry.filter(action=['edit_finish']))
