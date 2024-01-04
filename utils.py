from uuid import uuid4
from datetime import datetime


def make_uuid():
    return str(uuid4())


def to_datetime(datetime_str):
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

