from datetime import date, datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from db_api import api_requests
from create_bot import bot
from handlers._post import register_handlers_post
from handlers._delete import del_callback, register_delete
from handlers._put import register_put
from handlers._report_to import register_handlers_report_to
from handlers._get import register_handlers_get
from handlers._report import register_handlers_report
from handlers._start import register_handlers_start
from keyboards.all import kb_main_menu


# Прервать любое "состояние".
async def cancel_handlers(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('Отмена произошла успешно', reply_markup=kb_main_menu())


# Регистрация в диспетчере.
def register_handlers(disp: Dispatcher):

    # Отмена любого "состояния".
    disp.register_message_handler(cancel_handlers, Text(equals='Отмена', ignore_case=True), state='*')

    # Старт.
    # ГОТОВО
    register_handlers_start(disp)

    # Email.
    # ГОТОВО
    register_handlers_report_to(disp)

    # Отчет.
    # ГОТОВО
    register_handlers_report(disp)

    # Запись.
    # ГОТОВО
    register_handlers_post(disp)

    # Вывод записей.
    # ГОТОВО
    register_handlers_get(disp)

    # Изменение.
    # ГОТОВО
    register_put(disp)

    # Удаление.
    # ГОТОВО
    register_delete(disp)
