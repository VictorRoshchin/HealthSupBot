from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from create_bot import bot
from db_api import api_requests
from handlers._report_to import FSMReportTo
from keyboards.all import kb_main_menu, kb_email_or_telegram


async def command_start(message: types.Message):
    '''
    This handler is run the first time the user starts.
    :param message: the command "/start"
    :return: nothing
    '''

    await bot.send_message(message.from_user.id,
                           'Бот разработан для ведения дневника давления\n'
                           'Поддерживаемый функционал:\n'
                           '/Запись - создание записи в журнале и сохранение в базе данных\n'
                           '/Выгрузить - выгрузка записей из базы данных для просмотра, редактирования и удаления\n'
                           # '/Удалить - удалить запись из базы данных\n'
                           # '/Изменить - изменить запись\n'
                           '/Отчет - составить отчет и отправить на электронную почту\n')
    try:
        report_to = await api_requests.get(message.from_user.id, report_to=True)
        await message.answer(f'Вы выбрали метод получения отчета: {report_to}',
                             reply_markup=kb_main_menu())

    except:
        await FSMReportTo.report_to.set()
        await message.answer('Для начала мне нужно, чтобы вы сообщили, куда вы хотите получать отчеты',
                             reply_markup=kb_email_or_telegram())


def register_handlers_start(disp: Dispatcher):

    disp.register_message_handler(command_start, commands=['start'])

