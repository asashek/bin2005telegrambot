import config
import rasp
import exams_rasp

import datetime
import os
import random
import sqlite3
import os.path

import telebot
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

conn = sqlite3.connect('homework.db', check_same_thread=False)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS hw(
    id INTEGER,
    lesson TEXT,
    task TEXT);
""")
conn.commit()


@bot.message_handler(commands=['start'])
def start(message):
    action_pick = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    rasp = types.KeyboardButton('Расписание пар')
    exam_rasp = types.KeyboardButton('Расписание экзаменов')
    books = types.KeyboardButton('Учебная литература')
    action_pick.add(rasp, books, exam_rasp)

    bot.send_message(message.chat.id, 'Выбери то, что хочешь увидеть',
                     reply_markup=action_pick, parse_mode='HTML')



@bot.message_handler(content_types=['text'])
def action_pick(message):
    if message.text == 'Расписание пар':

        user_name = message.from_user.first_name

        day_pick_rasp = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        today = types.KeyboardButton('Сегодня')
        tomorrow = types.KeyboardButton('Завтра')
        this_week = types.KeyboardButton('На неделю')
        day_pick_rasp.add(today, tomorrow, this_week)


        day_pick_send = bot.send_message(message.chat.id, 'Привет, выбери, на какой день хочешь узнать расписание',
                                         reply_markup=day_pick_rasp)

        bot.register_next_step_handler(day_pick_send, day_check)


    elif message.text == 'Учебная литература':
        literature_pick = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        english = types.KeyboardButton('Английский язык')
        ikg = types.KeyboardButton('ИКГ')
        math = types.KeyboardButton('Математика')
        physics = types.KeyboardButton('Физика')

        literature_pick.add(english, math, physics, ikg)

        literature_pick_send = bot.send_message(message.chat.id, '<b>Выбери нужный предмет</b>', reply_markup=literature_pick,parse_mode="HTML")

        bot.register_next_step_handler(literature_pick_send, literature)

    elif message.text == 'Расписание экзаменов':
        bot.send_message(message.chat.id, exams_rasp.exam_rasp, parse_mode='HTML')

def day_check(message):
    today = str(datetime.date.today())
    today = today.split('-')

    if message.text == 'Сегодня':
        bot.send_message(message.chat.id, 'Расписание на сегодня')

        now_week_number = datetime.date(int(today[0]), int(today[1]), int(today[2])).isocalendar()[1]
        today_day_number = datetime.datetime.today().weekday()
        if today_day_number > 6:
            today_day_number -= 7
        if  today_day_number == 6:
            bot.send_message(message.chat.id, '<b><i>Это выходной день, пар нет</i></b>', parse_mode='HTML')
        else:
            if now_week_number % 2 == 0:
                bot.send_message(message.chat.id, rasp.Chet[today_day_number], parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, rasp.Nechet[today_day_number], parse_mode='HTML')

        start(message)

    elif message.text == 'Завтра':
        bot.send_message(message.chat.id, 'Расписание на завтра')

        now_week_number = datetime.date(int(today[0]), int(today[1]), int(today[2])).isocalendar()[1]
        today_day_number = datetime.datetime.today().weekday() + 1

        if today_day_number > 6:
            today_day_number -= 7
            now_week_number += 1
        if today_day_number == 6:
            bot.send_message(message.chat.id, '<b><i>Это выходной день, пар нет</i></b>', parse_mode='HTML')
        else:
            if now_week_number % 2 == 0:
                bot.send_message(message.chat.id, rasp.Chet[today_day_number], parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(message.chat.id, rasp.Nechet[today_day_number], parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())

        start(message)

    elif message.text == 'На неделю':

        now_week_number = datetime.date(int(today[0]), int(today[1]), int(today[2])).isocalendar()[1]

        today_day_number = datetime.datetime.today().weekday()

        other_day_markup = types.InlineKeyboardMarkup(row_width=3)

        mon = types.InlineKeyboardButton('Понедельник', callback_data='mon')
        tue = types.InlineKeyboardButton('Вторник', callback_data='tue')
        wed = types.InlineKeyboardButton('Среда', callback_data='wed')
        thu = types.InlineKeyboardButton('Четверг', callback_data='thu')
        fri = types.InlineKeyboardButton('Пятница', callback_data='fri')
        sat = types.InlineKeyboardButton('Суббота', callback_data='sat')
        other_day_markup.add(mon, tue, wed, thu, fri, sat)

        sm = ['(ノಠ益ಠ)ノ彡', '╭∩╮(Ο_Ο)╭∩╮', '(ಠ_ಠ)┌∩┐', 'ε(´סּ︵סּ`)з', 'Загрузка... ████████████] 99%']

        sm_id = random.randint(0, 4)

        if today_day_number > 5:
            now_week_number = datetime.date(int(today[0]), int(today[1]), int(today[2])).isocalendar()[1] + 1
            bot.send_message(message.chat.id, 'Выбери нужный день следующей недели', reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, 'День недели', reply_markup=other_day_markup)

        else:
            bot.send_message(message.chat.id, 'Выбери нужный день этой недели', reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, 'День недели', reply_markup=other_day_markup)

        @bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            rasp_day = ''
            try:
                if call.message:
                    if call.data == 'mon':
                        if now_week_number % 2 == 0:
                            bot.send_message(call.message.chat.id, rasp.Chet[0], parse_mode='HTML')
                        else:
                            bot.send_message(call.message.chat.id, rasp.Nechet[0], parse_mode='HTML')
                        rasp_day = "понедельник"

                    elif call.data == 'tue':
                        if now_week_number % 2 == 0:
                            bot.send_message(call.message.chat.id, rasp.Chet[1], parse_mode='HTML')
                        else:
                            bot.send_message(call.message.chat.id, rasp.Nechet[1], parse_mode='HTML')
                        rasp_day = "вторник"

                    elif call.data == 'wed':
                        if now_week_number % 2 == 0:
                            bot.send_message(call.message.chat.id, rasp.Chet[2], parse_mode='HTML')
                        else:
                            bot.send_message(call.message.chat.id, rasp.Nechet[2], parse_mode='HTML')
                        rasp_day = "среду"

                    elif call.data == 'thu':
                        if now_week_number % 2 == 0:
                            bot.send_message(call.message.chat.id, rasp.Chet[3], parse_mode='HTML')
                        else:
                            bot.send_message(call.message.chat.id, rasp.Nechet[3], parse_mode='HTML')
                        rasp_day = "четверг"

                    elif call.data == 'fri':
                        if now_week_number % 2 == 0:
                            bot.send_message(call.message.chat.id, rasp.Chet[4], parse_mode='HTML')
                        else:
                            bot.send_message(call.message.chat.id, rasp.Nechet[4], parse_mode='HTML')
                        rasp_day = "пятницу"

                    elif call.data == 'sat':
                        if now_week_number % 2 == 0:
                            bot.send_message(call.message.chat.id, rasp.Chet[5], parse_mode='HTML')
                        else:
                            bot.send_message(call.message.chat.id, rasp.Nechet[5], parse_mode='HTML')
                        rasp_day = "субботу"


                start(message)

            except Exception as e:
                print(repr(e))

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="<b>Расписание на " + rasp_day + ":</b>", reply_markup=None, parse_mode='HTML')


def literature(message):
    if message.text == 'Английский язык':
        files = os.listdir(path="./static/literature/english")
        for i in range(len(files)):
            book = open('static/literature/english/' + files[i], 'rb')
            bot.send_document(message.chat.id, book)

    elif message.text == 'Математика':
        files = os.listdir(path="./static/literature/math")
        for i in range(len(files)):
            book = open('static/literature/math/' + files[i], 'rb')
            bot.send_document(message.chat.id, book)

    elif message.text == 'Физика':
        files = os.listdir(path="./static/literature/physics")
        for i in range(len(files)):
            book = open('static/literature/physics/' + files[i], 'rb')
            bot.send_document(message.chat.id, book)

    elif message.text == 'ИКГ':
        files = os.listdir(path="./static/literature/ikg")
        for i in range(len(files)):
            book = open('static/literature/ikg/' + files[i], 'rb')
            bot.send_document(message.chat.id, book)
    start(message)


bot.polling(none_stop=True)
