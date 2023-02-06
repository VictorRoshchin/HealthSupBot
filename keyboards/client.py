from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

b1 = KeyboardButton('Запись')
b2 = KeyboardButton('Выгрузить')
b3 = KeyboardButton('Редактировать')

b5 = KeyboardButton('Отчет')
b6 = KeyboardButton('Отмена')
b7 = KeyboardButton('Изменить email')

kb_client_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client_start.row(b1, b2).row(b3, b5).row(b7)

kb_client_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client_cancel.add(b6)

kb_client_del = InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить'))

yes = KeyboardButton('Да')
no = KeyboardButton('Нет')
cancel = KeyboardButton('Отмена')
yes_or_no = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(yes, no, cancel)
