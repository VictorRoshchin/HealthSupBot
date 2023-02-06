from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from validate_email import validate_email

from bot_db import bot_sqlite
from create_bot import bot
from keyboards.client import kb_client_start


class FSMEmail(StatesGroup):
    email = State()


async def set_email(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    is_valid = validate_email(message.text)
    if not is_valid:
        await message.reply('Неккортный адрес электронной почты, попробуйте снова')
        await FSMEmail.email.set()
    else:
        async with state.proxy() as data:
            data['email'] = message.text
        user_table = await bot_sqlite.sql_user_table(user_id)
        if user_table:
            await bot_sqlite.sql_save_email(state, user_id)
        else:
            await bot_sqlite.sql_add_user(state, user_id)
        await state.finish()
        await message.reply('Электронная почта успешно сохранена', reply_markup=kb_client_start)


async def edit_email(message: types.Message):
    await bot.send_message(message.from_user.id, 'Напишите новый адрес электронной почты')
    await FSMEmail.email.set()
