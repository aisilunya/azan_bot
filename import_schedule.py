import csv
from model import Schedule
from sqlalchemy.orm import sessionmaker
from create import *
Session = sessionmaker(bind=engine)
importfile = "shedule_2016.csv"
session = Session()

with open (importfile, newline = '\n') as csvfile:
        csvreader = csv.reader(csvfile, delimiter = ',')
        for row in csvreader:
            keyslist1 = [row[1], row[2]]
            keyslist2 = [row[1], row[3]]
            keyslist3 = [row[1], row[4]]
            keyslist4 = [row[1], row[5]]
            keyslist5 = [row[1], row[6]]
            keyslist6 = [row[1], row[7]]
            keyslist7 = [row[1], row[8]]
            keys1 = ' '.join(keyslist1)
            keys2 = ' '.join(keyslist2)
            keys3 = ' '.join(keyslist3)
            keys4 = ' '.join(keyslist4)
            keys5 = ' '.join(keyslist5)
            keys6 = ' '.join(keyslist6)
            keys7 = ' '.join(keyslist7)

            h = Schedule(row[0], keys1, keys2, keys3, keys4, keys5, keys6, keys7)
            session.add(h)
session.commit()
