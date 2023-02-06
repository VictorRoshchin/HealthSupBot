import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage

import openpyxl

import os
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate


async def attach_file(msg, filepath):                             # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)                   # Получаем только имя файла
    ctype, encoding = mimetypes.guess_type(filepath)        # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:               # Если тип файла не определяется
        ctype = 'application/octet-stream'                  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)                 # Получаем тип и подтип
    if maintype == 'text':                                  # Если текстовый файл
        with open(filepath) as fp:                          # Открываем файл для чтения
            file = MIMEText(fp.read(), _subtype=subtype)    # Используем тип MIMEText
            fp.close()                                      # После использования файл обязательно нужно закрыть
    elif maintype == 'image':                               # Если изображение
        with open(filepath, 'rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'audio':                               # Если аудио
        with open(filepath, 'rb') as fp:
            file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
    else:                                                   # Неизвестный тип файла
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)              # Используем общий MIME-тип
            file.set_payload(fp.read())                     # Добавляем содержимое общего типа (полезную нагрузку)
            fp.close()
            encoders.encode_base64(file)                    # Содержимое должно кодироваться как Base64
    file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки
    msg.attach(file)                                        # Присоединяем файл к сообщению


async def send_email(to_email, file):

    # Сервер и данные бота.
    server = 'smtp.mail.ru'
    port = 25
    from_addr = 'healthsupbot@mail.ru'
    passwd = '46MchTvfmAujbVdr5akY'

    # server = 'smtp.gmail.com'
    # port = 587
    # from_addr = 'HealthSupBot@gmail.com'
    # passwd = 'Q!w2e3r4'

    # формируем тело письма
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg['To'] = to_email
    msg["Subject"] = 'Отчет'
    msg["Date"] = formatdate(localtime=True)

    await attach_file(msg, file)

    smtp = None
    try:
        smtp = smtplib.SMTP(server, port)
        smtp.starttls()
        smtp.login(from_addr, passwd)
        smtp.send_message(msg)
    except smtplib.SMTPException as err:
        print('Что - то пошло не так...')
        raise err
    finally:
        smtp.quit()


async def get_report(entries: list, user_id):
    etrs = [list(e)[:-1] for e in entries]
    # for e in etrs:
    #     date, time = e[3].split()
    #     e[3] = date
    #     e[4] = time
    header = ['Верхнее давление', 'Нижнее давление', 'Пульс', 'Дата', 'Время']
    report = openpyxl.Workbook()
    report.create_sheet(title='Отчет', index=0)
    table = report['Отчет']
    for row in range(1, len(etrs) + 2):
        if row == 1:
            for col in range(1, len(header)+1):
                value = header[col-1]
                cell = table.cell(row=row, column=col)
                cell.value = value
        else:
            for col in range(1, len(etrs[row-2])+1):
                value = etrs[row-2][col-1]
                cell = table.cell(row=row, column=col)
                cell.value = value
    report.save(f'report_{user_id}.xlsx')
    return f'report_{user_id}.xlsx'


async def send_report(entries_all, user_id, email):
    report = await get_report(entries_all, user_id)
    await send_email(email, report)
    os.remove(f'./{report}')
