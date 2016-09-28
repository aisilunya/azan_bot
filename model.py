from sqlalchemy import MetaData
from sqlalchemy.types import *
from sqlalchemy import Column
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from datetime import datetime as dt, timedelta

Base = declarative_base()


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    city = Column(String(50))
    fajr=Column(DateTime(timezone=False))
    voshod_solnsa=Column(DateTime(timezone=False))
    dhuhr = Column(DateTime(timezone=False))
    hanafi = Column(DateTime(timezone=False))
    shafigi = Column(DateTime(timezone=False))
    magrib =Column(DateTime(timezone=False))
    isha = Column(DateTime(timezone=False))
    __table_args__ = (UniqueConstraint('city', 'fajr', 'voshod_solnsa','dhuhr', 'hanafi', 'shafigi', 'magrib', 'isha'),)

    def __init__(self, city, fajr, voshod_solnsa, dhuhr, hanafi, shafigi, magrib, isha):

        self.city = city
        self.fajr = fajr
        self.voshod_solnsa = voshod_solnsa
        self.dhuhr = dhuhr
        self.hanafi = hanafi
        self.shafigi = shafigi
        self.magrib = magrib
        self.isha = isha


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    chat_id = Column(Integer)
    city = Column(String)
    name = Column (String)
    user_id = Column (Integer)
    alarm = Column(Boolean())
    last_sended = Column(DateTime(timezone=False), default='1970-01-01')
    __table_args__ = (UniqueConstraint('user_id'), )

    def __init__(self, chat_id, city, name, user_id, alarm=False, last_sended='1970-01-01'):
        self.chat_id = chat_id
        self.city = city
        self.name = name
        self.user_id = user_id
        self.alarm = alarm
        self.last_sended = last_sended