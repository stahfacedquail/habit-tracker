from modules.utils import make_uuid
from datetime import datetime, timedelta
from modules.utils import get_as_gmt


today = get_as_gmt(datetime.today())
start = today - timedelta(days=18)

habits = [
    (make_uuid(), "Jog", "daily", start.replace(hour=14, minute=25, second=58).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), "Phone parents", "weekly", start.replace(hour=8, minute=49, second=14).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), "Read a novel", "daily", start.replace(hour=16, minute=18, second=54).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), "Journal", "weekly", start.replace(hour=15, minute=6, second=39).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), "isiXhosa lesson", "weekly", start.replace(hour=23, minute=13, second=56).strftime("%Y-%m-%d %H:%M:%S")),
]

activities = [
    (make_uuid(), habits[0][0], (start + timedelta(days=1)).replace(hour=5, minute=8, second=28).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=2)).replace(hour=10, minute=23, second=32).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=4)).replace(hour=7, minute=53, second=16).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=5)).replace(hour=17, minute=15, second=5).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=10)).replace(hour=5, minute=12, second=24).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=11)).replace(hour=17, minute=30, second=58).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=12)).replace(hour=18, minute=51, second=6).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=13)).replace(hour=19, minute=59, second=43).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=16)).replace(hour=19, minute=58, second=55).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[0][0], (start + timedelta(days=17)).replace(hour=19, minute=37, second=26).strftime("%Y-%m-%d %H:%M:%S")),

    (make_uuid(), habits[1][0], start.replace(hour=16, minute=45, second=13).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[1][0], (start + timedelta(days=3)).replace(hour=11, minute=33, second=47).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[1][0], (start + timedelta(days=8)).replace(hour=13, minute=8, second=4).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[1][0], (start + timedelta(days=10)).replace(hour=18, minute=5, second=18).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[1][0], (start + timedelta(days=16)).replace(hour=15, minute=12, second=35).strftime("%Y-%m-%d %H:%M:%S")),

    (make_uuid(), habits[2][0], (start + timedelta(days=5)).replace(hour=12, minute=28, second=52).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[2][0], (start + timedelta(days=6)).replace(hour=8, minute=24, second=52).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[2][0], (start + timedelta(days=7)).replace(hour=7, minute=18, second=34).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[2][0], (start + timedelta(days=12)).replace(hour=15, minute=43, second=49).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[2][0], (start + timedelta(days=15)).replace(hour=17, minute=3, second=10).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[2][0], (start + timedelta(days=16)).replace(hour=6, minute=25, second=32).strftime("%Y-%m-%d %H:%M:%S")),

    (make_uuid(), habits[3][0], (start + timedelta(days=13)).replace(hour=22, minute=17, second=43).strftime("%Y-%m-%d %H:%M:%S")),

    (make_uuid(), habits[4][0], (start + timedelta(days=5)).replace(hour=19, minute=23, second=57).strftime("%Y-%m-%d %H:%M:%S")),
    (make_uuid(), habits[4][0], (start + timedelta(days=15)).replace(hour=19, minute=30, second=0).strftime("%Y-%m-%d %H:%M:%S")),
]
