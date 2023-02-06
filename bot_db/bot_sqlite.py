import sqlite3 as sq
from datetime import datetime, date, time

from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect('health.db')
    cur = base.cursor()
    base.execute('CREATE TABLE IF NOT EXISTS users(user_id CHAR PRIMARY KEY, email CHAR)')
    base.commit()
    if base:
        print('DB connected!')


async def sql_add_user(state, user_id):
    async with state.proxy() as data:
        email = data['email']
        cur.execute(f'INSERT INTO users (user_id, email) VALUES(?, ?)', tuple((user_id, email)))
        base.commit()


async def sql_user_table(user_id):
    return cur.execute(f'SELECT EXISTS (SELECT * FROM users WHERE user_id={user_id})').fetchone()[0]


async def sql_save_email(state, user_id):
    async with state.proxy() as data:
        email = data['email']
    cur.execute(f'UPDATE users SET email="{email}" WHERE user_id={user_id}')
    base.commit()


async def get_user_email(user_id):
    return cur.execute(f'SELECT email FROM users WHERE user_id={user_id}').fetchone()[0]


async def create_table(message):
    table = f'''CREATE TABLE IF NOT EXISTS health_{message.from_user.id}(
                     top_pressure TEXT, 
                     lower_pressure TEXT, 
                     pulse TEXT,
                     comment TEXT,
                     entry_date DATE,
                     entry_time TIME,
                     id INTEGER PRIMARY KEY)'''
    base.execute(table)
    base.commit()


async def sql_add_command(state, message):
    async with state.proxy() as data:
        data['entry_date'] = str(datetime.today().date())
        data['entry_time'] = str(datetime.today().time())
        cur.execute(f'INSERT INTO health_{message.from_user.id}'
                    f'(top_pressure, lower_pressure, pulse, comment, entry_date, entry_time)'
                    f'VALUES (?, ?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()


# async def sql_show_command(message):
#     for ret in cur.execute(f'SELECT * FROM health_{message.from_user.id}').fetchall():
#         await bot.send_message(message.from_user.id, f'Вехнее давление: {ret[0]}\nНижнее давление: {ret[1]}\nПульс: {ret[2]},\nДата: {datetime.strptime(ret[3], "%d.%m.%Y %H:%M"):%d.%m.%Y %H:%M}')


async def sql_get_all_command(user_id, count=None):
    if count is None:
        return cur.execute(f'SELECT * FROM health_{user_id} ORDER BY entry_date DESC, entry_time DESC').fetchall()
    else:
        return cur.execute(f'SELECT * FROM health_{user_id} ORDER BY entry_date DESC, entry_time DESC LIMIT {count}').fetchall()


async def sql_get_report(user_id, date_from=None, date_to=datetime.today().date()):
    if date_from:
        return cur.execute(f'''
                    SELECT * FROM `health_{user_id}` 
                    WHERE entry_date BETWEEN "{date_from}" AND "{date_to}"
                    ORDER BY entry_date DESC, entry_time DESC
        ''').fetchall()
    else:
        return cur.execute(f'SELECT * FROM `health_{user_id}`').fetchall()


async def sql_get_user_email(user_id):
    return cur.execute(f'SELECT email FROM users WHERE user_id={user_id}')


async def sql_del_command(data, table):
    cur.execute(f'DELETE FROM health_{table} WHERE id == ?', (data,))
    base.commit()


async def sql_update_command(user_id, entry_id, top_pressure, lower_pressure, pulse):
    cur.execute(f'UPDATE health_{user_id} SET top_pressure={top_pressure}, lower_pressure={lower_pressure}, pulse={pulse} WHERE id={entry_id}')
    base.commit()


async def sql_get_begin_date(user_id):
    return cur.execute(f'SELECT MIN(entry_date) FROM health_{user_id}').fetchone()[0]
