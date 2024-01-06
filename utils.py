from uuid import uuid4
from datetime import datetime
from math import floor


def make_uuid():
    """
    Generate a random UUID.
    :return: A stringified UUID
    """
    return str(uuid4())


def to_datetime(datetime_str):
    """
    Take a date/time string and convert into a datetime object
    :param datetime_str: e.g. "2023-10-05 12:00:54", which is how dates are stored in the database
    :return: The corresponding datetime object
    """
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def to_date_only_string(dt: datetime):
    """
    Get a date-only string from `dt`, a datetime object.
    """
    return dt.strftime("%Y-%m-%d")


def strip_out_time(dt: datetime):
    """
    "Remove" the time bit from a datetime object (pretty much set the time to 00:00:00).
    :return: A new datetime object where the time has been stripped off
    """
    return datetime(year=dt.year, month=dt.month, day=dt.day)


def get_num_days_from_to(start_date: datetime, end_date: datetime):
    """
    Count the number of days from `start_date` up to and including `end_date`.
    :param start_date: e.g. 2023-12-25 12:00:21
    :param end_date: e.g. 2024-01-12 08:12:12
    :return: e.g. 19
    """
    start_date_ignoring_time = strip_out_time(start_date)
    end_date_ignoring_time = strip_out_time(end_date)
    return (end_date_ignoring_time - start_date_ignoring_time).days + 1


def get_num_weeks_from_to(start_of_begin_week: datetime, start_of_end_week: datetime):
    """
    Count the number of weeks from the week that starts at `start_of_begin_week` up to and including the week that
    starts at `start_of_end_week`.
    :param start_of_begin_week: e.g. 2023-12-27 12:00:21
    :param start_of_end_week: e.g. 2024-03-13 08:12:12
    :return: 12
    """
    start_date_ignoring_time = strip_out_time(start_of_begin_week)
    end_date_ignoring_time = strip_out_time(start_of_end_week)
    return floor((end_date_ignoring_time - start_date_ignoring_time).days/7) + 1

