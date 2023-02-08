from contextlib import suppress

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from db_api import api_requests
from create_bot import bot
from keyboards.all import kb_main_menu, kb_choice


# Состояние изменения записи.
class FSMChange(StatesGroup):
    entries = State()


# Для временного хранения id.
entry_change = None


async def pressure_validation(pressure):
    try:
        pressure = int(pressure)
        if pressure >= 310 or pressure < 30:
            return False
        return True
    except:
        return False


class FSMHealthPut(StatesGroup):
    top_pressure = State()
    lower_pressure = State()
    pulse = State()
    add_comment = State()
    comment = State()
    save = State()


async def put_entry(call: types.CallbackQuery):
    global entry_id
    entry_id = call.data.replace('put_entry ', '')
    print(entry_id)
    await FSMHealthPut.top_pressure.set()
    await call.message.answer('Введите значение верхнего давления', reply_markup=kb_choice(cancel=True))
    await call.answer()


# Запись верхнего давления в состояние.
async def put_entry_top(message: types.Message, state: FSMContext):

    is_valid = await pressure_validation(message.text)

    if is_valid:
        await state.update_data(top_pressure=message.text)
        await state.set_state(FSMHealthPut.lower_pressure.state)
        await message.answer('Теперь запишите нижнее давление', reply_markup=kb_choice(cancel=True))
    else:
        await message.answer('Значение должно быть целым положительным числом в пределах 30...310')


# Запись нижнего давление в состояние.
async def put_entry_lower(message: types.Message, state: FSMContext):

    is_valid = await pressure_validation(message.text)

    if is_valid:
        await state.update_data(lower_pressure=message.text)
        await state.set_state(FSMHealthPut.pulse.state)
        await message.answer('Запишите пульс', reply_markup=kb_choice(cancel=True))
    else:
        await message.answer('Значение должно быть целым положительным числом в пределах 30...310')


async def put_entry_pulse(message: types.Message, state: FSMContext):

    is_valid = await pressure_validation(message.text)

    if is_valid:
        await state.update_data(pulse=message.text)
        await state.set_state(FSMHealthPut.add_comment.state)
        await message.answer('Хотите оставить комментарий к записи?',
                             reply_markup=kb_choice(yes_and_no=True, cancel=True))
    else:
        await message.answer('Значение должно быть целым положительным числом в пределах 30...310')


# Запись пульса в состояние.
async def put_entry_add_comment(message: types.Message, state: FSMContext):

    if message.text == 'Да':
        await state.set_state(FSMHealthPut.comment.state)
        await message.answer('Оставьте комментарий', reply_markup=kb_choice(cancel=True))

    elif message.text == 'Нет':
        await state.update_data(comment='')
        entry_date = await state.get_data()
        top_pressure = entry_date['top_pressure']
        lower_pressure = entry_date['lower_pressure']
        pulse = entry_date['pulse']
        await state.set_state(FSMHealthPut.save.state)
        await message.answer(f'Занести показания {top_pressure}/{lower_pressure}-{pulse} в журнал?',
                             reply_markup=kb_choice(yes=True, again=True, cancel=True))

    else:
        await message.answer('Пожалуйста, используйте кнопки, которые находятся под полем для ввода текста')


async def put_entry_comment(message: types.Message, state: FSMContext):

    await state.update_data(comment=message.text)

    entry_date = await state.get_data()
    top_pressure = entry_date['top_pressure']
    lower_pressure = entry_date['lower_pressure']
    pulse = entry_date['pulse']
    await state.set_state(FSMHealthPut.save.state)
    await message.answer(f'Занести показания {top_pressure}/{lower_pressure}-{pulse} в журнал?\n'
                         f'Комментарий к записи: {message.text}',
                         reply_markup=kb_choice(yes=True, again=True, cancel=True))


async def put_entry_save(message: types.Message, state: FSMContext):

    await message.answer(message.text)

    if message.text == 'Да':

        entry = await state.get_data()

        entry.update({'entry_id': entry_id})

        await state.finish()
        await api_requests.put(message.from_user.id, entry=entry)
        await message.answer('Запись успешно изменена', reply_markup=kb_main_menu())

    elif message.text == 'Изменить':
        await message.answer('Запишите верхнее давление', reply_markup=kb_choice(cancel=True))
        await state.set_state(FSMHealthPut.top_pressure.state)

    else:
        await message.answer('Пожалуйста, используйте кнопки, которые находятся под полем для ввода текста')


def register_put(disp: Dispatcher):
    disp.register_callback_query_handler(put_entry, lambda x: x.data.startswith('put_entry'))
    disp.register_message_handler(put_entry_top, state=FSMHealthPut.top_pressure)
    disp.register_message_handler(put_entry_lower, state=FSMHealthPut.lower_pressure)
    disp.register_message_handler(put_entry_pulse, state=FSMHealthPut.pulse)
    disp.register_message_handler(put_entry_add_comment, state=FSMHealthPut.add_comment)
    disp.register_message_handler(put_entry_comment, state=FSMHealthPut.comment)
    disp.register_message_handler(put_entry_save, state=FSMHealthPut.save)
