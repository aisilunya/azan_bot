from sqlalchemy import Table, Column, INTEGER, String, MetaData, ForeignKey
from sqlalchemy.types import *
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from model import Schedule, Users, Base
import json

with open("config.json") as json_file:
    config = json.load(json_file)

engine = create_engine(config['database']['dsn'], echo=True)
metadata = Base.metadata
metadata.create_all(engine)