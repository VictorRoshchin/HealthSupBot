from datetime import date, datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from bot_db import bot_sqlite
from create_bot import bot
from handlers._create_entry import command_diary_entry, load_lower, load_top, load_pulse, FSMHealth, \
    register_handlers_adder
from handlers._delete_entry import del_callback, register_deleter
from handlers._edit_entry import register_editor
from handlers._email import set_email, FSMEmail, edit_email
from handlers._get_entry import register_handlers_getter
from handlers._report import register_handlers_report
from handlers._start import command_start
from keyboards.client import kb_client_start


# Прервать любое "состояние".
async def cancel_handlers(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Отмена произошла успешно', reply_markup=kb_client_start)


# Регистрация в диспетчере.
def register_handlers_client(disp: Dispatcher):

    # Отмена любого "состояния".
    disp.register_message_handler(cancel_handlers, Text(equals='Отмена', ignore_case=True), state='*')

    # Старт.
    disp.register_message_handler(command_start, commands=['start'])
    disp.register_message_handler(set_email, state=FSMEmail.email)

    # Изменить email.
    disp.register_message_handler(edit_email, Text(equals='Изменить email', ignore_case=True))

    # Запись.
    register_handlers_adder(disp)

    # Вывод записей.
    register_handlers_getter(disp)

    # Изменение.
    register_editor(disp)

    # Удаление.
    register_deleter(disp)

    # Отчет.
    register_handlers_report(disp)

