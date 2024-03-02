from modules.utils import make_uuid
from datetime import datetime, timedelta


today = datetime.today()
start = today - timedelta(days=18)

day = []  # dates from `start` until 17 days later
for index in range(18):
    day.append(start + timedelta(days=index))


def date_to_string(dt: datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


habits = [
    (make_uuid(), "Jog", "daily", date_to_string(day[0].replace(hour=14, minute=25, second=58))),
    (make_uuid(), "Phone parents", "weekly", date_to_string(day[0].replace(hour=8, minute=49, second=14))),
    (make_uuid(), "Read a novel", "daily", date_to_string(day[0].replace(hour=16, minute=18, second=54))),
    (make_uuid(), "Journal", "weekly", date_to_string(day[0].replace(hour=15, minute=6, second=39))),
    (make_uuid(), "isiXhosa lesson", "weekly", date_to_string(day[0].replace(hour=23, minute=13, second=56))),
]

activities = [
    (make_uuid(), habits[0][0], date_to_string(day[1].replace(hour=5, minute=8, second=28))),
    (make_uuid(), habits[0][0], date_to_string(day[2].replace(hour=10, minute=23, second=32))),
    (make_uuid(), habits[0][0], date_to_string(day[4].replace(hour=7, minute=53, second=16))),
    (make_uuid(), habits[0][0], date_to_string(day[5].replace(hour=17, minute=15, second=5))),
    (make_uuid(), habits[0][0], date_to_string(day[10].replace(hour=5, minute=12, second=24))),
    (make_uuid(), habits[0][0], date_to_string(day[11].replace(hour=17, minute=30, second=58))),
    (make_uuid(), habits[0][0], date_to_string(day[12].replace(hour=18, minute=51, second=6))),
    (make_uuid(), habits[0][0], date_to_string(day[13].replace(hour=19, minute=59, second=43))),
    (make_uuid(), habits[0][0], date_to_string(day[16].replace(hour=19, minute=58, second=55))),
    (make_uuid(), habits[0][0], date_to_string(day[17].replace(hour=19, minute=37, second=26))),

    (make_uuid(), habits[1][0], date_to_string(day[0].replace(hour=16, minute=45, second=13))),
    (make_uuid(), habits[1][0], date_to_string(day[3].replace(hour=11, minute=33, second=47))),
    (make_uuid(), habits[1][0], date_to_string(day[8].replace(hour=13, minute=8, second=4))),
    (make_uuid(), habits[1][0], date_to_string(day[10].replace(hour=18, minute=5, second=18))),
    (make_uuid(), habits[1][0], date_to_string(day[16].replace(hour=15, minute=12, second=35))),

    (make_uuid(), habits[2][0], date_to_string(day[5].replace(hour=12, minute=28, second=52))),
    (make_uuid(), habits[2][0], date_to_string(day[6].replace(hour=8, minute=24, second=52))),
    (make_uuid(), habits[2][0], date_to_string(day[7].replace(hour=7, minute=18, second=34))),
    (make_uuid(), habits[2][0], date_to_string(day[12].replace(hour=15, minute=43, second=49))),
    (make_uuid(), habits[2][0], date_to_string(day[15].replace(hour=17, minute=3, second=10))),
    (make_uuid(), habits[2][0], date_to_string(day[16].replace(hour=6, minute=25, second=32))),

    (make_uuid(), habits[3][0], date_to_string(day[13].replace(hour=22, minute=17, second=43))),

    (make_uuid(), habits[4][0], date_to_string(day[5].replace(hour=19, minute=23, second=57))),
    (make_uuid(), habits[4][0], date_to_string(day[15].replace(hour=19, minute=30, second=0))),
]
