from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from validate_email import validate_email

from db_api import api_requests
from create_bot import bot
from keyboards.all import kb_email_or_telegram, kb_main_menu


class FSMReportTo(StatesGroup):
    report_to = State()
    email = State()


async def get_report_to(message: types.Message, state: FSMContext):

    if message.text == 'email':
        await state.finish()
        await FSMReportTo.email.set()
        await message.answer('Напишите адрес эллектронной почты')

    elif message.text == 'telegram':
        await state.finish()
        try:
            await api_requests.post(message.from_user.id, user_data={'report_to': 'telegram'})
        except:
            await api_requests.put(message.from_user.id, user_data={'report_to': 'telegram'})
        finally:
            report_to = await api_requests.get(message.from_user.id, report_to=True)
            await message.answer(f'Вы выбрали метод получения отчета: {report_to}',
                                 reply_markup=kb_main_menu())

    else:
        await message.answer('Пожалуйста, используйте кнопки',
                             reply_markup=kb_email_or_telegram())


async def report_to_email(message: types.Message, state: FSMContext):
    is_valid = validate_email(message.text)
    if not is_valid:
        await message.reply('Некорректный адрес электронной почты, попробуйте снова')
    else:
        try:
            await api_requests.get(message.from_user.id, report_to=True)
            await api_requests.put(message.from_user.id, user_data={'report_to': message.text})
        except:
            await api_requests.post(message.from_user.id, user_data={'report_to': message.text})
        finally:
            await state.finish()
            await message.answer(f'Электронная почта {message.text} успешно сохранена',
                                 reply_markup=kb_main_menu())


async def info_report_to(message: types.Message):

    try:
        report_to = await api_requests.get(message.from_user.id, report_to=True)

        if report_to == 'telegram':
            answer = await message.answer(f'Вы выбрали метод получения отчета по телеграмму')
            message_id = answer.message_id
            await message.answer(
                'Возможные действия:',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text='Изменить', callback_data=f'report_to_put '
                                                                        f'{message_id}'),
                    InlineKeyboardButton(text='Закрыть действия', callback_data=f'report_to_exit '
                                                                                f'{report_to} '
                                                                                f'{message_id}'
                                         )
                )
            )

        else:
            answer = await message.answer(f'Вы выбрали метод получения отчета по email {report_to}')
            message_id = answer.message_id
            await message.answer(
                'Возможные действия:',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text='Изменить', callback_data=f'report_to_put '
                                                                        f'{message_id}'),
                    InlineKeyboardButton(text='Закрыть действия', callback_data=f'report_to_exit '
                                                                                f'{report_to} '
                                                                                f'{message_id}')
                )
            )

    except:
        await FSMReportTo.report_to.set()
        await message.answer(
            'Необходимо выбрать способ получения отчета',
            reply_markup=kb_email_or_telegram()
        )


async def report_to_put(call: types.CallbackQuery):

    message_id = int(call.data.split()[1])
    await bot.delete_message(call.message.chat.id, message_id)

    await call.message.delete()
    await FSMReportTo.report_to.set()
    await call.message.answer('Куда вы хотите получать отчеты', reply_markup=kb_email_or_telegram())
    await call.answer()


async def report_to_exit(call: types.CallbackQuery):
    report_to = call.data.split()[1]
    message_id = int(call.data.split()[2])
    await bot.delete_message(call.message.chat.id, message_id)

    await call.message.delete()

    if report_to == 'telegram':
        await call.message.answer(f'Вы выбрали метод получения отчета по телеграмму',
                                  reply_markup=kb_main_menu())

    else:
        await call.message.answer(f'Вы выбрали метод получения отчета по email {report_to}',
                                  reply_markup=kb_main_menu())


def register_handlers_report_to(disp: Dispatcher):

    # Выбор способа получения отчета.
    disp.register_message_handler(get_report_to, state=FSMReportTo.report_to)

    # Изменить email.
    disp.register_message_handler(report_to_email, state=FSMReportTo.email)

    # Информация о способе получения отчета.
    disp.register_message_handler(info_report_to, Text(equals='Способ отчета', ignore_case=True))

    # Изменение способа получения отчета.
    disp.register_callback_query_handler(report_to_put, lambda x: x.data.startswith('report_to_put'))

    # Изменение способа получения отчета.
    disp.register_callback_query_handler(report_to_put, lambda x: x.data.startswith('report_to_put'))

    # Закрыть информацию о способе получения отчета.
    disp.register_callback_query_handler(report_to_exit, lambda x: x.data.startswith('report_to_exit'))
