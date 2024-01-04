from uuid import uuid4
from datetime import datetime


def make_uuid():
    return str(uuid4())


def to_datetime(datetime_str):
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def get_num_days_from_to(start_date: datetime, end_date: datetime):
    start_date_ignoring_time = datetime(year=start_date.year, month=start_date.month, day=start_date.day)
    end_date_ignoring_time = datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    return (end_date_ignoring_time - start_date_ignoring_time).days + 1


def is_same_day(date_a: datetime, date_b: datetime):
    return date_a.year == date_b.year and date_a.month == date_b.month and date_a.day == date_b.day
