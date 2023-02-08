from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

b1 = KeyboardButton('Запись')
b2 = KeyboardButton('Выгрузить')
b3 = KeyboardButton('Редактировать')

b5 = KeyboardButton('Отчет')
b6 = KeyboardButton('Отмена')
b7 = KeyboardButton('Способ отчета')


kb_delete = InlineKeyboardMarkup().add(InlineKeyboardButton('Удалить'))


def kb_choice(**kwargs):

    choice = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

    if kwargs.get('yes_and_no', False):
        yes = KeyboardButton('Да')
        no = KeyboardButton('Нет')
        choice.add(yes, no)

    if kwargs.get('yes', False):
        yes = KeyboardButton('Да')
        choice.add(yes)

    if kwargs.get('cancel', False):
        cancel = KeyboardButton('Отмена')
        choice.add(cancel)

    if kwargs.get('again', False):
        again = KeyboardButton('Изменить')
        choice.add(again)

    return choice


def kb_main_menu(**kwargs):
    kb_main = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    post = KeyboardButton('Запись')
    get = KeyboardButton('Выгрузить')
    report = KeyboardButton('Отчет')
    report_info = KeyboardButton('Способ отчета')

    kb_main.row(post, get).row(report, report_info)

    return kb_main


def kb_email_or_telegram(**kwargs):

    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    bt_email = KeyboardButton('email')
    bt_telegram = KeyboardButton('telegram')
    kb.row(bt_email, bt_telegram)

    if kwargs.get('main_menu', False):
        bt_main_menu = KeyboardButton('Главное меню')
        kb.add(bt_main_menu)

    return kb


def kb_get_count(**kwargs):

    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)

    counter = kwargs.get('counter', '')

    bt_last = KeyboardButton('Последнюю')

    kb.insert(bt_last)

    if counter:
        counter = int(counter)
        if counter <= 10:
            bt_all = KeyboardButton('Все записи')
            kb.add(bt_all)
            return kb
        else:
            bt_ten = KeyboardButton('Последние 10')
            bt_count = KeyboardButton('Ввести количество')
            kb.insert(bt_ten)
            kb.insert(bt_count)
            return kb
