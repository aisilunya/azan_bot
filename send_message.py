import json
import telebot
import logging
from sqlalchemy import create_engine, Date, Time, cast, func
from model import Users, Schedule, Base
from sqlalchemy.orm import sessionmaker
from datetime import date, time, timezone
from datetime import datetime as dt, timedelta


def send_message(bot, session):
    users_alarm = session.query(Users). \
        filter(Users.alarm == True). \
        filter(Users.last_sended < dt.now() - timedelta(minutes=5)).all()

    for user in users_alarm:

        user_schedule = session.query(Schedule). \
            filter(cast(Schedule.hanafi, Date) == date.today()). \
            filter(Schedule.city == Users.city).first()

        list_schedule = [user_schedule.fajr, user_schedule.voshod_solnsa, user_schedule.dhuhr, user_schedule.hanafi, user_schedule.shafigi,
                         user_schedule.magrib, user_schedule.isha]
        time_intervals = []
        intervals={}
        for time in list_schedule:
            interval = time - dt.now()
            time_intervals += [interval]

        list_closer = []

        for interval in time_intervals:
            if interval.days != -1:
                list_closer += [interval]

        if len(list_closer) == 0:
            return

        min_time = min(list_closer)

        intervals['Фаджр'] = time_intervals[0]
        intervals['Восход солнца'] = time_intervals[1]
        intervals['Зухр'] = time_intervals[2]
        intervals['Аср по первой тени'] = time_intervals[3]
        intervals['Аср по второй тени'] = time_intervals[4]
        intervals['Магриб'] = time_intervals[5]
        intervals['Иша'] = time_intervals[6]

        for key in intervals:
            if intervals[key] == min_time and  min_time.seconds <= 5 * 60:
                bot.send_message(user.chat_id, text='{name} через  5 минут '.format(name=key))
                user.last_sended = dt.now()
                session.commit()


if __name__ == '__main__':
    with open("config.json") as json_file:
        config = json.load(json_file)

    engine = create_engine(config['database']['dsn'], echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    token = config["telegram"]["token"]
    bot = telebot.TeleBot(token)
    send_message(bot, session)
