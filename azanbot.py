import json
from telebot import types
import telebot
import logging
from sqlalchemy import create_engine, Date, Time, cast, select
from model import Users, Schedule
from sqlalchemy.orm import sessionmaker
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from datetime import date, time, timezone
from datetime import datetime as dt, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


with open("config.json") as json_file:
    config = json.load(json_file)

engine = create_engine(config['database']['dsn'], echo=True)
Session = sessionmaker(bind=engine)
session = Session()


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

token = config["telegram"]["token"]
bot = telebot.TeleBot(token)

@bot.message_handler(commands = ['start'])
def start(message):
    name = message.from_user.username
    markup = types.ReplyKeyboardMarkup()
    markup.row('Список городов', 'Помощь')
    markup.row('Расписание намаза','Ближайший намаз')
    markup.row('Подписаться или отписаться от рассылки')
    bot.send_message(message.chat.id, """Ассаляму 'алейкум, {name}! Выберите одну из комманд.""".format(name=name), reply_markup = markup)

@bot.message_handler(regexp = "Список городов")
def get_city(message):
    name = message.from_user.username
    query = select([Schedule.city]). \
        group_by(Schedule.city)
    result = session.execute(query).fetchall()
    cities = [c[0] for c in result]


    keyboard = types.InlineKeyboardMarkup()

    for city in cities:

        c_button = types.InlineKeyboardButton(text = city, callback_data =city)
        keyboard.add(c_button)
    bot.send_message(message.chat.id, "Выберите Ваш город, пожалуйста!", reply_markup = keyboard)

@bot.message_handler(regexp = "Помощь")
def help(message):
    bot.send_message(message.chat.id, text='Используйте кнопку "Список городов"  для получения списка городов, для которых есть расписание намаза\n '
                                                '"Расписание намаза" для получения расписания намаза на сегодня\n'
                                                '"Ближайший намаз"  чтобы узнать сколько времени осталось для ближайшего намаза\n'
                                                '"Подписаться или отписаться от рассылки" чтобы получать напоминания о намазе от бота за 5 минут до каждого намаза')
@bot.callback_query_handler(func = lambda call: True)
def set_city(call):
    text = call.data

    name = call.from_user.username
    user_id = call.from_user.id
    chat_id = user_id
    print(text)


    city = text

    query = select([Schedule.city]).\
                    group_by(Schedule.city)
    result = session.execute(query).fetchall()
    cities = [c[0] for c in result]
    if city in cities:
        user = session.query(Users).filter(Users.user_id == user_id).first()

        if user is None:
            user = Users(chat_id = chat_id, city=city, name = name, user_id=user_id)
            session.add(user)
            session.commit()
            bot.answer_callback_query(callback_query_id= call.id, show_alert=True, text = 'Вы выбрали город {name1}, {name2}'.format(name1= city,name2=name))

        else:
            new_city = city
            user.city = new_city
            session.commit()
            bot.answer_callback_query(callback_query_id= call.id, show_alert = True, text='Настройки сохранены, {name1}. Вы выбрали город {name2}'.format(name1=name, name2 = city))

    else:
        bot.answer_callback_query(callback_query_id=call.id, show_alert = True, text='Такого города нет, {name}'.format(name=name))

@bot.message_handler(regexp = "Расписание намаза")
def get_schedule(message):
    user_id = message.from_user.id
    user = session.query(Users).filter(Users.user_id == user_id).first()
    if user is None:
        bot.send_message(message.chat.id, text= " Сначала выберите ,пожалуйста, город.")
    else:
        user_schedule = session.query(Schedule). \
            filter(cast(Schedule.fajr, Date) == date.today()). \
            filter(Schedule.city == user.city).first()

        user_schedule.fajr11 = dt.strftime(user_schedule.fajr, "%H:%M")
        user_schedule.fajr22 = dt.strftime(user_schedule.fajr, "%Y.%m.%d")
        user_schedule.voshod_solnsa1 = dt.strftime(user_schedule.voshod_solnsa, "%H:%M")
        user_schedule.dhuhr1 = dt.strftime(user_schedule.dhuhr, "%H:%M")
        user_schedule.hanafi1= dt.strftime(user_schedule.hanafi, "%H:%M")
        user_schedule.shafigi1 = dt.strftime(user_schedule.shafigi, "%H:%M")
        user_schedule.magrib1 = dt.strftime(user_schedule.magrib, "%H:%M")
        user_schedule.isha1 = dt.strftime(user_schedule.isha, "%H:%M")
        bot.send_message(message.chat.id,
                        text="Расписание намаза на сегодня %s для города %s: \n Фаджр %s\n Восход солнца %s\n Зауаль %s\n Аср по первой тени %s\n Аср по второй тени %s\n Магриб %s\n Иша %s" %
                            (user_schedule.fajr22,user_schedule.city, user_schedule.fajr11, user_schedule.voshod_solnsa1, user_schedule.dhuhr1, user_schedule.hanafi1,
                            user_schedule.shafigi1, user_schedule.magrib1, user_schedule.isha1))
@bot.message_handler(regexp= 'Ближайший намаз')
def get_closertime(message):
    user_id = message.from_user.id
    user = session.query(Users).filter(Users.user_id == user_id).first()
    if user is None:
        bot.send_message(message.chat.id, text= "Сначала выберите, пожалуйста, город")
    else:
        user_schedule = session.query(Schedule). \
            filter(cast(Schedule.hanafi, Date) == date.today()). \
            filter(Schedule.city == user.city).first()
        list_schedule = [user_schedule.fajr, user_schedule.voshod_solnsa, user_schedule.dhuhr, user_schedule.hanafi, user_schedule.shafigi, user_schedule.magrib,user_schedule.isha]
        intervals = []
        for time in list_schedule:
            interval = time-dt.now()
            intervals += [interval]

        list_closer=[]
        dict = {}
        for interval in intervals:
            if interval.days != -1:
                list_closer +=[interval]

        if len(list_closer) == 0:
            bot.send_message(message.chat.id, text= 'Следующий намаз завтра')
            return
        min_time = min(list_closer)



        dict['Фаджр'] = intervals[0]
        dict['Восход солнца'] = intervals[1]
        dict['Зауаль'] = intervals[2]
        dict['Аср по первой тени'] = intervals[3]
        dict['Аср по второй тени'] = intervals[4]
        dict['Магриб'] = intervals[5]
        dict['Иша'] = intervals[6]

        for key in dict:
            if dict[key] == min_time:
                change_time = ':'.join(str(min_time).split(':')[:2])
                if change_time[0] == '0':
                    bot.send_message(message.chat.id, text='Следующий намаз {n} через {name[2]}{name[3]} минут(ы)'.format(n = key, name=change_time))
                else:
                    bot.send_message(message.chat.id,
                                     text='Следующий намаз {n} через {name[0]} час(ов) {name[2]}{name[3]} минут(ы)'.format(
                                         n=key, name=change_time))
        return


@bot.message_handler(regexp= 'Подписаться или отписаться от рассылки')
def set_alarm(message):
    user_id = message.from_user.id
    user = session.query(Users).filter(Users.user_id == user_id).first()
    if user is None:
        bot.send_message(message.chat.id, text= "Сначала выберите, пожалуйста, город")
    else:
        user.alarm = not user.alarm
        session.commit()
        if user.alarm == True:
            bot.send_message(message.chat.id, text='Вы подписаны на рассылку напоминаний о намазе. Мы отправим Вам сообщение за 5 минут до начала.')
        else:
            bot.send_message(message.chat.id, text='Вы отписаны от рассылки напоминаний о намазе')


if __name__ == '__main__':
    bot.polling(none_stop= True)