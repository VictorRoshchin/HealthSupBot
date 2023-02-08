import sqlite3 as sq
from datetime import datetime, date, time

from create_bot import bot


def db_start():
    '''
    Creates a global variables - a base (database) and a cur (cursor to db).
    Connects to the base and create a users table if it doesn't exist.
    :return: nothing.
    '''
    global base, cur
    base = sq.connect('health.db')
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS users(user_id CHAR PRIMARY KEY, report_to CHAR)')
    base.commit()
    if base:
        print('DB connected!')


async def get(user_id, **kwargs):
    '''

    :param user_id: for identification user table
    :param kwargs: for parameterize a get request
            count: int - get a certain number of records
            date_from: date - for clarify the report period
            date_to: date - in addition to date_from
            first_entry_date: bool - for get a first date of the entry
            email: str - for get a user email
    :return:
    '''
    count = kwargs.get('count', False)
    entry_count = kwargs.get('entry_count', False)
    date_from = kwargs.get('date_from', False)
    first_entry_date = kwargs.get('first_entry_date', False)
    report_to = kwargs.get('report_to', False)
    entry_check = kwargs.get('entry_check', False)

    if count:
        return cur.execute(
            f'SELECT * FROM health_{user_id} ORDER BY entry_date DESC, entry_time DESC LIMIT {count}').fetchall()

    elif entry_count:
        return cur.execute(f'SELECT COUNT(*) FROM health_{user_id}').fetchone()[0]

    elif entry_check:
        try:
            check = cur.execute(f'SELECT * FROM health_{user_id} WHERE id="{entry_check}"').fetchone()[0]
            return True
        except:
            return False

    elif date_from:
        date_to = kwargs.get('date_to', datetime.today().date())
        return cur.execute(f'''
                    SELECT * FROM `health_{user_id}` 
                    WHERE entry_date BETWEEN "{date_from}" AND "{date_to}"
                    ORDER BY entry_date DESC, entry_time DESC
        ''').fetchall()

    elif first_entry_date:
        return cur.execute(f'SELECT MIN(entry_date) FROM health_{user_id}').fetchone()[0]

    elif report_to:
        return cur.execute(f'SELECT report_to FROM users WHERE user_id="{user_id}"').fetchone()[0]

    else:
        return cur.execute(f'SELECT * FROM health_{user_id} ORDER BY entry_date DESC, entry_time DESC').fetchall()


async def post(user_id, **kwargs):

    '''

    :param user_id:
    :param kwargs:
    :return:
    '''

    entry = kwargs.get('entry')

    user_data = kwargs.get('user_data')

    create_table = kwargs.get('create_table', False)

    if entry:
        top_pressure = entry.get('top_pressure')
        lower_pressure = entry.get('lower_pressure')
        pulse = entry.get('pulse')
        comment = entry.get('comment')
        entry_date = str(datetime.today().date())
        entry_time = str(datetime.today().time())

        cur.execute(f'INSERT INTO health_{user_id}'
                    f'(top_pressure, lower_pressure, pulse, comment, entry_date, entry_time) '
                    f'VALUES("{top_pressure}", "{lower_pressure}", "{pulse}", "{comment}", "{entry_date}", "{entry_time}")')
        base.commit()

    elif user_data:
        report_to = user_data.get('report_to')
        cur.execute(f'INSERT INTO users (`user_id`, `report_to`) VALUES("{user_id}", "{report_to}")')
        base.commit()

    elif create_table:
        cur.execute(f'CREATE TABLE IF NOT EXISTS health_{user_id}'
                    f'(top_pressure TEXT,'
                    f'lower_pressure TEXT,'
                    f'pulse TEXT,'
                    f'comment TEXT,'
                    f'entry_date DATE,'
                    f' entry_time TIME,'
                    f'id INTEGER PRIMARY KEY AUTOINCREMENT)')
    # elif sort.get('user_date', False):


async def put(user_id, **kwargs):

    '''

    :param user_id:
    :param kwargs:
    :return:
    '''

    entry = kwargs.get('entry', dict())

    user_data = kwargs.get('user_data', dict())

    if entry:
        entry_id = entry.get('entry_id')
        top_pressure = entry.get('top_pressure')
        lower_pressure = entry.get('lower_pressure')
        pulse = entry.get('pulse')
        comment = entry.get('comment')
        cur.execute(f'UPDATE health_{user_id} '
                    f'SET top_pressure="{top_pressure}", lower_pressure="{lower_pressure}", pulse="{pulse}" '
                    f'WHERE id={entry_id}')
        base.commit()

    elif user_data:
        report_to = user_data.get('report_to')
        cur.execute(f'UPDATE users SET report_to="{report_to}" WHERE user_id="{user_id}"')
        base.commit()


async def delete(user_id, **kwargs):

    entry_id = kwargs.get('entry_id', False)

    if entry_id:
        cur.execute(f'DELETE FROM health_{user_id} WHERE id="{entry_id}"')
        base.commit()


# async def sql_user_table(user_id):
#     return cur.execute(f'SELECT EXISTS (SELECT * FROM users WHERE user_id={user_id})').fetchone()[0]


# async def create_table(message):
#     '''
#     Create table in the DB if it doesn't exist.
#     :param message:
#     :return:
#     '''
#     table = f'''CREATE TABLE IF NOT EXISTS health_{message.from_user.id}(
#                      top_pressure TEXT,
#                      lower_pressure TEXT,
#                      pulse TEXT,
#                      comment TEXT,
#                      entry_date DATE,
#                      entry_time TIME,
#                      id INTEGER PRIMARY KEY)'''
#     base.execute(table)
#     base.commit()


# async def sql_show_command(message):
#     for ret in cur.execute(f'SELECT * FROM health_{message.from_user.id}').fetchall():
#         await bot.send_message(message.from_user.id, f'Вехнее давление: {ret[0]}\nНижнее давление: {ret[1]}\nПульс: {ret[2]},\nДата: {datetime.strptime(ret[3], "%d.%m.%Y %H:%M"):%d.%m.%Y %H:%M}')
