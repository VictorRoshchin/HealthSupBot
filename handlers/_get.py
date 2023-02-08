from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db_api import api_requests
from create_bot import bot
from keyboards.all import kb_main_menu, kb_get_count, kb_choice


class FSMGetEntry(StatesGroup):
    show = State()
    count = State()


async def get_entry_print(message: types.Message, count=1):

    entries = await api_requests.get(message.from_user.id, count=count)

    for e in entries:
        await bot.send_message(message.from_user.id,
                               f'Дата: {".".join(reversed(e[4].split("-")))}, время: {e[5][:5]}\n'
                               f'Вехнее давление: {e[0]}\n'
                               f'Нижнее давление: {e[1]}\n'
                               f'Пульс: {e[2]}\n'
                               f'Комментарий: {e[3]}',
                               reply_markup=InlineKeyboardMarkup().add(
                                   InlineKeyboardButton(text='Изменить', callback_data=f'put_entry {e[-1]}'),
                                   InlineKeyboardButton(text='Удалить', callback_data=f'delete_entry {e[-1]}')
                               ))


async def get_entry(message: types.Message):
    entry_count = await api_requests.get(message.from_user.id, entry_count=True)
    if int(entry_count) == 0:
        await message.answer('У вас нет ни одной записи. Добавьте запись, нажав кнопку "Запись", находящуюся под '
                             'полем для ввода текста', reply_markup=kb_main_menu())
    else:
        await FSMGetEntry.show.set()
        await message.reply('Сколько записей выгрузить?', reply_markup=kb_get_count(counter=entry_count))


async def get_entry_show(message: types.Message, state: FSMContext):

    entry_count = await api_requests.get(message.from_user.id, entry_count=True)
    entry_count = int(entry_count)

    if message.text == 'Последнюю':
        await get_entry_print(message)
        await message.answer('Выгружена последняя запись', reply_markup=kb_main_menu())
        await state.finish()

    elif message.text == 'Последние 10':
        await get_entry_print(message, count=10)
        await message.answer('Выгружены последние 10 записей', reply_markup=kb_main_menu())
        await state.finish()

    elif message.text == 'Ввести количество':

        await state.set_state(FSMGetEntry.count.state)

        if entry_count > 20:
            await state.update_data(max_count=20)
            await message.answer('Введите целое число. В целях рационального использования ресурсов сервера и '
                                 'телеграмма, количество выгружаемых записей ограничено 20',
                                 reply_markup=kb_choice(cancel=True))

        else:
            await state.update_data(max_count=entry_count)
            await message.answer(f'Введите целое число. Вы можете вывести максимум {entry_count} записей',
                                 reply_markup=kb_choice(cancel=True))

    elif message.text == 'Все записи':
        await get_entry_print(message, count=entry_count)
        await message.answer(f'Выгружены все записи ({entry_count})', reply_markup=kb_main_menu())
        await state.finish()
    else:
        await message.answer('Пожалуйста, используйте кнопки, которые находятся под полем для ввода текста')


async def get_entry_count(message: types.Message, state: FSMContext):

    count = message.text

    try:
        count = int(count)
        data = await state.get_data()
        max_count = data.get('max_count')
        if count > max_count:
            await message.answer(f'Введите целое число. Вы можете вывести максимум {max_count} записей',
                                 reply_markup=kb_choice(cancel=True))
        else:
            await get_entry_print(message, count=count)
            await message.answer(f'Выгружено {count} записей', reply_markup=kb_main_menu())
            await state.finish()
    except:
        await message.answer('Введите целое число', reply_markup=kb_choice(cancel=True))


def register_handlers_get(disp: Dispatcher):

    disp.register_message_handler(get_entry, Text(equals='Выгрузить', ignore_case=True))

    disp.register_message_handler(get_entry_show, state=FSMGetEntry.show)

    disp.register_message_handler(get_entry_count, state=FSMGetEntry.count)
