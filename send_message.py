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
        intervals = []
        interval_dict={}
        for time in list_schedule:
            interval = time - dt.now()
            intervals += [interval]

        list_closer = []

        for interval in intervals:
            if interval.days != -1:
                list_closer += [interval]

        if len(list_closer) == 0:
            return

        min_time = min(list_closer)

        interval_dict['Фаджр'] = intervals[0]
        interval_dict['Восход солнца'] = intervals[1]
        interval_dict['Зауаль'] = intervals[2]
        interval_dict['Аср по первой тени'] = intervals[3]
        interval_dict['Аср по второй тени'] = intervals[4]
        interval_dict['Магриб'] = intervals[5]
        interval_dict['Иша'] = intervals[6]

        for key in interval_dict:
            if interval_dict[key] == min_time and  min_time.seconds <= 5 * 60:
                bot.send_message(user.chat_id, text='Следующий намаз {name} через  5 минут '.format(name=key))
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
