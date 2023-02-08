from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import db_api.api_requests
from db_api import api_requests
from create_bot import bot
from keyboards.all import kb_main_menu, kb_choice

TABLE = False


class FSMHealthPost(StatesGroup):
    top_pressure = State()
    lower_pressure = State()
    pulse = State()
    add_comment = State()
    comment = State()
    save = State()




health_cb = CallbackData('comment', 'action', 'top_pressure', 'lower_pressure', 'pulse')


async def pressure_validation(pressure):
    try:
        pressure = int(pressure)
        if pressure >= 310 or pressure < 30:
            return False
        return True
    except:
        return False


# Начать запись (состоние записи).
async def post_entry(message: types.Message):
    await api_requests.post(message.from_user.id, create_table=True)
    await FSMHealthPost.top_pressure.set()
    await message.answer('Запишите верхнее давление', reply_markup=kb_choice(cancel=True))


# Запись верхнего давления в состояние.
async def post_entry_top(message: types.Message, state: FSMContext):

    is_valid = await pressure_validation(message.text)

    if is_valid:
        await state.update_data(top_pressure=message.text)
        await state.set_state(FSMHealthPost.lower_pressure.state)
        await message.answer('Теперь запишите нижнее давление', reply_markup=kb_choice(cancel=True))
    else:
        await message.answer('Значение должно быть целым положительным числом в пределах 30...310')


# Запись нижнего давление в состояние.
async def post_entry_lower(message: types.Message, state: FSMContext):

    is_valid = await pressure_validation(message.text)

    if is_valid:
        await state.update_data(lower_pressure=message.text)
        await state.set_state(FSMHealthPost.pulse.state)
        await message.answer('Запишите пульс', reply_markup=kb_choice(cancel=True))
    else:
        await message.answer('Значение должно быть целым положительным числом в пределах 30...310')


async def post_entry_pulse(message: types.Message, state: FSMContext):

    is_valid = await pressure_validation(message.text)

    if is_valid:
        await state.update_data(pulse=message.text)
        await state.set_state(FSMHealthPost.add_comment.state)
        await message.answer('Хотите оставить комментарий к записи?', reply_markup=kb_choice(yes_and_no=True,
                                                                                             cancel=True))
    else:
        await message.answer('Значение должно быть целым положительным числом в пределах 30...310')


# Запись пульса в состояние.
async def post_entry_add_comment(message: types.Message, state: FSMContext):

    if message.text == 'Да':
        await state.set_state(FSMHealthPost.comment.state)
        await bot.send_message(message.from_user.id, 'Оставьте комментарий', reply_markup=kb_choice(cancel=True))

    elif message.text == 'Нет':
        await state.update_data(comment='')
        entry_date = await state.get_data()
        top_pressure = entry_date['top_pressure']
        lower_pressure = entry_date['lower_pressure']
        pulse = entry_date['pulse']
        await state.set_state(FSMHealthPost.save.state)
        await bot.send_message(message.from_user.id,
                               f'Занести показания {top_pressure}/{lower_pressure}-{pulse} в журнал?',
                               reply_markup=kb_choice(yes=True, again=True, cancel=True))

    else:
        await message.answer('Пожалуйста, используйте кнопки, которые находятся под полем для ввода текста')


async def post_entry_comment(message: types.Message, state: FSMContext):

    await state.update_data(comment=message.text)
    entry_date = await state.get_data()
    top_pressure = entry_date['top_pressure']
    lower_pressure = entry_date['lower_pressure']
    pulse = entry_date['pulse']
    await state.set_state(FSMHealthPost.save.state)
    await bot.send_message(message.from_user.id,
                           f'Занести показания {top_pressure}/{lower_pressure}-{pulse} в журнал?\n'
                           f'Комментарий к записи: {message.text}',
                           reply_markup=kb_choice(yes=True, again=True, cancel=True))


async def post_entry_save(message: types.Message, state: FSMContext):

    if message.text == 'Да':

        entry = await state.get_data()
        await state.finish()
        await db_api.api_requests.post(message.from_user.id, entry=entry)
        await message.answer('Запись успешно добавлена', reply_markup=kb_main_menu())

    elif message.text == 'Изменить':
        await message.answer('Запишите верхнее давление', reply_markup=kb_choice(cancel=True))
        await state.set_state(FSMHealthPost.top_pressure.state)


def register_handlers_post(disp: Dispatcher):
    disp.register_message_handler(post_entry, Text(equals='Запись', ignore_case=True), state=None)
    disp.register_message_handler(post_entry_top, state=FSMHealthPost.top_pressure)
    disp.register_message_handler(post_entry_lower, state=FSMHealthPost.lower_pressure)
    disp.register_message_handler(post_entry_pulse, state=FSMHealthPost.pulse)
    disp.register_message_handler(post_entry_add_comment, state=FSMHealthPost.add_comment)
    disp.register_message_handler(post_entry_comment, state=FSMHealthPost.comment)
    disp.register_message_handler(post_entry_save, state=FSMHealthPost.save)
