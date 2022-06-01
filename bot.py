import datetime
import re
import subprocess
from datetime import datetime, timedelta
import asyncio
import time
from threading import Thread

import telebot
from telebot import types

from db import add_to_db_tasklist, read_data_in_task, init_db, change_tz, get_user_tz, add_user, user_time, show_tasks, delete_task, all_task
from WorkWithText import time_1

bot = telebot.TeleBot('5570302869:AAFp_AUGpSyVMJ2Q5KEDFx-A3uw7DAtyb4w')

@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    tz_string = "+03"
    add_user(message.chat.id, tz_string)
    now_user_time = user_time(message.chat.id)
    bot.send_message(message.chat.id,
        f"Привет, я бот котрый напомнит тебе что то сделать. \n"
        f"Просто напиши мне что и когда тебе напомнить. \n"
        f"Например \"Выпить таблетки завтра днем\" или \"Забрать заказ 13 октября\"\n"
        f"Список напоминаний можно посмотреть с помощью команды /tasklist.\n"
        f"Я работаю в часовом поясе:{tz_string} (ставится по умолчанию)\n"
        f"У вас установлен часовой пояс {now_user_time}\n")

@bot.message_handler(commands=['tasklist'])
def start_message(message):
    bot.send_message(message.chat.id,
        f"/start. - описание бота\n"
        f"/tasklist - вывод всех команд\n"
        f"/settimezone - смена часового пояса \n"
        f"/mytask - Выводит ваши задачи"
        f"Если хотите удалить задачу напишите delete и номер задачи (пример 'delete 5')"
        f"Если хотите добавить задачу без напоминания просто напишите ее\n"
        f"Если вы хотите добавить задачу и напминиане, просто напишите сообщение в формате: HH:MM DD:MM:YYY\n")


@bot.message_handler(commands=['settimezone'])
def settimezone_message(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Изменить часовой пояс', callback_data='list_timezone'))
    timezone = 'Ваш часовой пояс ' + get_user_tz(message.chat.id)
    bot.send_message(message.chat.id, timezone, reply_markup=keyboard)

@bot.message_handler(commands=['mytask'])
def alltask(message):
    str = show_tasks(message.chat.id)
    bot.send_message(message.chat.id, f"Ваши задачи\n{str}")

@bot.message_handler(content_types=['text'])  # Функция обрабатывает текстовые сообщения
def in_text(message):
    user_timezone = get_user_tz(message.chat.id)
    message.text.lstrip()
    if len(message.text) < 17:
        if len(message.text) > 6:
            if message.text[:6] == 'delete':
                try:
                    count_task_str = message.text[6:]
                    count_task = int(count_task_str)
                    delete_task(count_task)
                    bot.send_message(message.chat.id, "Задача удалена")
                except:
                    bot.send_message(message.chat.id, "Неверно записано удаление задачи")
        else:
            add_to_db_tasklist(message.chat.id, message.text, '0', message.text)
            bot.send_message(message.chat.id, "Задача добавлена")
    else:
        time_str = message.text[:16]
        date = time_1(time_str)
        if date == None:
            bot.send_message(message.chat.id, "Неверный формат")
        else:
            task_text = message.text[16:]
            timezone = int(user_timezone) - 3
            date_now = datetime.now() + timedelta(hours = timezone)
            if datetime.now() > date_now:
                bot.send_message(message.chat.id, "Время уже прошло!")
            else:
                add_to_db_tasklist(message.chat.id, message.text, date, task_text)
                bot.send_message(message.chat.id, "Запись сделана")


@bot.callback_query_handler(func=lambda call: True)  # Реакция на кнопки
def callback(call):
    if call.data == 'list_timezone':
        list_timezone(call.message.chat.id)
    if call.data.startswith('set_timezone:'):
        timezone = call.data.split(':')[1]
        change_tz(call.message.chat.id, timezone)
        bot.send_message(call.message.chat.id, f"Ваш часовой пояс изменен на {timezone}")


def list_timezone(id):  #клавиатура выбора часовых поясов
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Europe/Moscow', callback_data='set_timezone:+03'))
    keyboard.add(types.InlineKeyboardButton(text='Europe/Kaliningrad', callback_data='set_timezone: +02'),
                 types.InlineKeyboardButton(text='Europe/Samara', callback_data='set_timezone: +04'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Yekaterinburg', callback_data='set_timezone: +05'),
                 types.InlineKeyboardButton(text='Asia/Omsk', callback_data='set_timezone: +06'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Krasnoyarsk', callback_data='set_timezone: +07'),
                 types.InlineKeyboardButton(text='Asia/Irkutsk', callback_data='set_timezone: +08'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Yakutsk', callback_data='set_timezone: +09'),
                 types.InlineKeyboardButton(text='Asia/Vladivostok', callback_data='set_timezone: +10'))
    keyboard.add(types.InlineKeyboardButton(text='Asia/Magadan', callback_data='set_timezone: +11'),
                 types.InlineKeyboardButton(text='Asia/Kamchatka', callback_data='set_timezone: +12'))
    bot.send_message(id, 'Выберите часовой пояс', reply_markup=keyboard)


class task1(Thread):
    print(1)
    arr = all_task()
    for i in range(len(arr)):
        now_user_tz = get_user_tz(arr[i][0])
        timezone = int(now_user_tz) - 3
        date_now = datetime.now() + timedelta(hours = timezone)
        if datetime.now() == date_now:
            bot.send_message(arr[i][0], arr[i][3])

class task2(Thread):
    print(2)
    bot.polling(none_stop=False, interval = 1)

if __name__ == '__main__':  # Ожидать входящие сообщения
    init_db()
    while True:
        t1 = task1()
        t1.start()
        t1.stop()
        t2 = task2()
        t2.start()
        t2.stop()
        time.sleep(1)

#async def send_message():

#        await asyncio.sleep(60)

#loop = asyncio.get_event_loop()
#loop.run_until_complete(send_message())
