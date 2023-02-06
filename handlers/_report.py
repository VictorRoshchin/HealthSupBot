from calendar import monthrange
from contextlib import suppress
from datetime import datetime, date
from time import strptime

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from bot_db import bot_sqlite
from create_bot import bot
from handlers._report_mail import send_report
from keyboards.client import kb_client_start

period_report = CallbackData('period_report', 'action', 'year', 'b_year', 'month', 'b_month', 'day', 'b_day', 'select_from')


async def get_period(message, limit: dict):
    with suppress(MessageNotModified):
        await message.edit_text(message.from_user.id, f'''Выбранный период:\n"
                                От: {limit['from']} до -{limit['to']}''')


# Формирование и отправка отчета.
async def get_report_command(message: types.Message):
    await message.reply('Сформатировать полный отчет или выбрать период?',
                        reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton(text='Полный отчет', callback_data='full'),
                            InlineKeyboardButton(text='Выбрать даты', callback_data=period_report.new(
                                action='get_year',
                                year='',
                                b_year='',
                                month='',
                                b_month='',
                                day='',
                                b_day='',
                                select_from='',
                            )),
                        ))


async def full_report(call: types.CallbackQuery):
    user_id = call.message.reply_to_message.from_user.id
    await call.answer(text='Формируем отчет')
    await call.message.delete()
    entries_all = await bot_sqlite.sql_get_report(user_id)
    email = await bot_sqlite.get_user_email(user_id)
    await send_report(entries_all, user_id, email)
    await bot.send_message(user_id, f'Отчет отправлен на электронную почту {email}',
                           reply_markup=kb_client_start)


async def get_keyboard_years(years, b_year, b_month, b_day, select_from, callback, action):
    kb = InlineKeyboardMarkup()
    for y in years:
        kb.insert(
            InlineKeyboardButton(text=str(y), callback_data=callback.new(
                action=action,
                year=y, b_year=b_year,
                month=b_month, b_month=b_month,
                day=b_day, b_day=b_day,
                select_from=select_from
            ))
        )
    return kb


async def period_from_year_report(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    select_from = callback_data.get('select_from', '')

    b_date = await bot_sqlite.sql_get_begin_date(user_id)

    b_year, b_month, b_day = map(int, str(b_date).split('-'))

    t_year, t_month, t_day = map(int, datetime.today().date().strftime("%Y %m %d").split())

    b_year = int(b_year)

    years = (y for y in range(b_year, int(t_year) + 1))

    kb = await get_keyboard_years(years, b_year, b_month, b_day, select_from, period_report, 'get_month')

    await bot.send_message(user_id, 'Выберите год', reply_markup=kb)


async def get_keyboard_months(months, year, b_year, b_month, b_day, select_from, callback, action):
    kb = InlineKeyboardMarkup()
    for m in months:
        kb.insert(
            InlineKeyboardButton(text=str(m), callback_data=callback.new(
                action=action,
                year=year, b_year=b_year,
                month=m, b_month=b_month,
                day=b_day, b_day=b_day,
                select_from=select_from
            ))
        )
    return kb


async def period_from_month_report(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    select_from = callback_data.get('select_from', '')
    year = int(callback_data['year'])
    b_year = int(callback_data['b_year'])
    b_month = int(callback_data['b_month'])
    b_day = int(callback_data['b_day'])

    t_year, t_month, t_day = map(int, datetime.today().date().strftime("%y %m %d").split())

    if year == b_year and year == t_year:
        months = (y for y in range(int(b_month), t_month + 1))
    elif year == b_year:
        months = (y for y in range(int(b_month), 13))
    elif year == t_year:
        months = (y for y in range(1, t_month + 1))
    else:
        months = (y for y in range(1, 13))

    kb = await get_keyboard_months(months, year, b_year, b_month, b_day, select_from, period_report, 'get_day')

    await bot.send_message(user_id, 'Выберите месяц', reply_markup=kb)


async def get_keyboard_days(days, year, b_year, month, b_month, b_day, select_from, callback, action):
    kb = InlineKeyboardMarkup()
    for d in days:
        kb.insert(
            InlineKeyboardButton(text=str(d), callback_data=callback.new(
                action=action,
                year=year, b_year=b_year,
                month=month, b_month=b_month,
                day=d, b_day=b_day,
                select_from=select_from
            ))
        )
    return kb


async def period_from_day_report(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    select_from = callback_data.get('select_from', '')
    year = int(callback_data['year'])
    month = int(callback_data['month'])
    b_year = int(callback_data['b_year'])
    b_month = int(callback_data['b_month'])
    b_day = int(callback_data['b_day'])

    weekday, last_day = map(int, monthrange(year, month))

    t_year, t_month, t_day = map(int, datetime.today().date().strftime("%y %m %d").split())

    if month == b_month and month == t_month:
        days = range(b_day, t_day + 1)
    elif month == b_month:
        days = range(b_day, last_day + 1)
    elif month == t_month:
        days = range(1, t_day + 1)
    else:
        days = range(1, last_day+1)
    kb = await get_keyboard_days(days, year, b_year, month, b_month,
                                 b_day, select_from, period_report, 'accept_date_from')
    await bot.send_message(user_id, 'Выберите число', reply_markup=kb)


accept_from = CallbackData('p_from', 'action', 'date_append', 'select_from')


async def date_f(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()
    select_from = callback_data.get('select_from', '')
    day = callback_data['day']
    year = callback_data['year']
    month = callback_data['month']
    mth = [0, 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
           'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
    await bot.send_message(user_id, f'Выбран {year} год, {month} месяц ({mth[int(month)]}), {day} число',
                           reply_markup=InlineKeyboardMarkup()
                           .add(InlineKeyboardButton(text='Подтвердить',
                                                     callback_data=accept_from.new(
                                                         action='append_date_from',
                                                         date_append=f'{year}-{month}-{day}',
                                                         select_from=select_from
                                                     ))
                                )
                           .add(
                               InlineKeyboardButton(text='Изменить дату',
                                                    callback_data=period_report.new(
                                                        action='get_year',
                                                        year='',
                                                        b_year='',
                                                        month='',
                                                        b_month='',
                                                        day='',
                                                        b_day='',
                                                        select_from=select_from,

                                                    ))
                           ))


append_date = CallbackData('accept_date', 'action', 'date_to', 'date_from')


async def period_to(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.message.delete()
    await call.answer()

    yearf, monthf, dayf = callback_data["date_append"].split('-')
    date_append = f'{yearf}-{monthf.rjust(2, "0")}-{dayf.rjust(2, "0")}'

    select_from = callback_data.get('select_from', '')

    if select_from != '':
        yeart, montht, dayt = select_from.split('-')
        select_from = f'{yeart}-{montht.rjust(2, "0")}-{dayt.rjust(2, "0")}'
        await bot.send_message(user_id,
                               f'Отчет будет сформирован за период:'
                               f'От {select_from} до {date_append} включительно',
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(text='Подтвердить',
                                                        callback_data=append_date.new(
                                                            action='custom_report',
                                                            date_to=date_append,
                                                            date_from=select_from
                                                         )),
                                   InlineKeyboardButton(text='Изменить', callback_data=period_report.new(
                                       action='get_year',
                                       year='',
                                       b_year='',
                                       month='',
                                       b_month='',
                                       day='',
                                       b_day='',
                                       select_from=select_from,
                                   ))
                               ))
    else:
        await bot.send_message(user_id,
                               f'Выбрана начальная дата {date_append}.\n'
                               f'До какой даты включительно формировать отчет?',
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(text='До настоящего времени',
                                                        callback_data=accept_from.new(
                                                            action='current_report',
                                                            date_append=date_append,
                                                            select_from=''
                                                         )),
                                   InlineKeyboardButton(text='Выбрать дату', callback_data=period_report.new(
                                       action='get_year',
                                       year='',
                                       b_year='',
                                       month='',
                                       b_month='',
                                       day='',
                                       b_day='',
                                       select_from=date_append,
                                   ))
                               ))


async def to_current_report(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.answer(text='Формируем отчет')
    await call.message.delete()

    dt_str = callback_data["date_append"]
    # dt_str = f'{year}-{month.rjust(2, "0")}-{day.rjust(2, "0")}'
    entries = await bot_sqlite.sql_get_report(user_id, date_from=dt_str)
    email = await bot_sqlite.get_user_email(user_id)
    await send_report(entries, user_id, email)
    await bot.send_message(user_id, f'Отчет отправлен на электронную почту {email}')


async def to_custrom_report(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    await call.answer(text='Формируем отчет')
    await call.message.delete()
    df = callback_data["date_from"]
    # df = f'{yearf}-{monthf.rjust(2, "0")}-{dayf.rjust(2, "0")}'

    dt = callback_data["date_to"]
    # dt = f'{yeart}-{montht.rjust(2, "0")}-{dayt.rjust(2, "0")}'

    entries = await bot_sqlite.sql_get_report(user_id, date_from=df, date_to=dt)
    email = await bot_sqlite.get_user_email(user_id)
    await send_report(entries, user_id, email)
    await bot.send_message(user_id, f'Отчет отправлен на электронную почту {email}', reply_markup=kb_client_start)


def register_handlers_report(disp: Dispatcher):
    disp.register_message_handler(get_report_command, Text(equals='Отчет', ignore_case=True))

    # Полного отчета.
    disp.register_callback_query_handler(full_report, lambda x: x.data and x.data.startswith('full'))

    # Выбор периода.
    # Дата ОТ.
    disp.register_callback_query_handler(period_from_year_report, period_report.filter(action=['get_year']))
    disp.register_callback_query_handler(period_from_month_report, period_report.filter(action=['get_month']))
    disp.register_callback_query_handler(period_from_day_report, period_report.filter(action=['get_day']))
    # Подтверждение даты ОТ.
    disp.register_callback_query_handler(date_f, period_report.filter(action=['accept_date_from']))
    # Выбор даты ДО.
    disp.register_callback_query_handler(period_to, accept_from.filter(action=['append_date_from']))

    disp.register_callback_query_handler(to_current_report, accept_from.filter(action=['current_report']))
    disp.register_callback_query_handler(to_custrom_report, append_date.filter(action=['custom_report']))

    # disp.register_callback_query_handler(period_to_month_report, f_year.filter(action=['dt_year']))
    # disp.register_callback_query_handler(period_to_day_report, f_month.filter(action=['dt_month']))
    # disp.register_callback_query_handler(date_to, f_day.filter(action=['dt_day']))

