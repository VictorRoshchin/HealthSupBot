from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from bot_db import bot_sqlite
from create_bot import bot
from keyboards.client import kb_client_cancel, kb_client_start, yes_or_no

TABLE = False


class FSMHealth(StatesGroup):
    top = State()
    lower = State()
    pulse = State()
    answer = State()
    comment = State()
    final = State()


health_cb = CallbackData('comment', 'action', 'top', 'lower', 'pulse')


# Начать запись (состоние записи).
async def command_diary_entry(message: types.Message):
    global TABLE
    if not TABLE:
        await bot_sqlite.create_table(message)
        TABLE = True
    await FSMHealth.top.set()
    await bot.send_message(message.from_user.id, 'Запишите верхнее давление', reply_markup=kb_client_cancel)


# Запись верхнего давления в состояние.
async def load_top(message: types.Message, state: FSMContext):
    await state.update_data(top=message.text)
    await state.set_state(FSMHealth.lower.state)
    await bot.send_message(message.from_user.id, 'Теперь запишите нижнее давление', reply_markup=kb_client_cancel)
    await message.delete()


# Запись нижнего давление в состояние.
async def load_lower(message: types.Message, state: FSMContext):
    await state.update_data(lower=message.text)
    await state.set_state(FSMHealth.pulse.state)
    await bot.send_message(message.from_user.id, 'Запишите пульс', reply_markup=kb_client_cancel)
    await message.delete()


async def load_pulse(message: types.Message, state: FSMContext):
    await state.update_data(pulse=message.text)
    await state.set_state(FSMHealth.answer.state)
    await bot.send_message(message.from_user.id, 'Хотите оставить комментарий к записи?',
                           reply_markup=yes_or_no)
    await message.delete()


# Запись пульса в состояние.
async def load_answer(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Оставьте комментарий')
    if message.text == 'Да':
        await state.set_state(FSMHealth.comment.state)
    else:
        await state.update_data(comment='')
        entry_date = await state.get_data()
        top = entry_date['top']
        lower = entry_date['lower']
        pulse = entry_date['pulse']
        await state.set_state(FSMHealth.final.state)
        await bot.send_message(message.from_user.id,
                               f'Занести показания {top}/{lower}-{pulse} в журнал?',
                               reply_markup=yes_or_no)


async def load_comment(message: types.Message, state: FSMContext):

    await state.update_data(comment=message.text)
    entry_date = await state.get_data()
    top = entry_date['top']
    lower = entry_date['lower']
    pulse = entry_date['pulse']
    await state.set_state(FSMHealth.final.state)
    await bot.send_message(message.from_user.id,
                           f'Занести показания {top}/{lower}-{pulse} в журнал?\n'
                           f'Комментарий к записи: {message.text}',
                           reply_markup=yes_or_no)


async def load_final(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        await bot_sqlite.sql_add_command(state, message)
        await bot.send_message(message.from_user.id, 'Запись успешно добавлена', reply_markup=kb_client_start)
        await state.finish()
    else:
        await state.set_state(FSMHealth.top.state)


def register_handlers_adder(disp: Dispatcher):
    disp.register_message_handler(command_diary_entry, Text(equals='Запись', ignore_case=True), state=None)
    disp.register_message_handler(load_top, state=FSMHealth.top)
    disp.register_message_handler(load_lower, state=FSMHealth.lower)
    disp.register_message_handler(load_pulse, state=FSMHealth.pulse)
    disp.register_message_handler(load_answer, state=FSMHealth.answer)
    disp.register_message_handler(load_comment, state=FSMHealth.comment)
    disp.register_message_handler(load_final, state=FSMHealth.final)
