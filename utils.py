from uuid import uuid4
from datetime import datetime, timedelta
from functools import reduce

import utils


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


def to_date_string(dt: datetime):
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
    return (end_date_ignoring_time - start_date_ignoring_time).days/7 + 1


def is_next_day(date_a: datetime, date_b: datetime):
    """
    Check if `date_b` is on the day that follows `date_a`.
    :param date_a: e.g. 2023-12-27 12:00:21
    :param date_b: e.g. 2023-12-28 20:00:05
    :return: e.g. True
    """
    next_day = strip_out_time(date_a) + timedelta(days=1)
    return strip_out_time(date_b) == next_day


def is_next_week(start_of_week_for_date_a: datetime, date_b: datetime):
    """
    Check if `date_b` occurs in the week that follows the week starting with `start_of_week_for_date_a`
    :param start_of_week_for_date_a: e.g. 2023-12-27 12:00:21
    :param date_b: e.g. 2023-12-30 00:01:23
    :return: e.g. False
    """
    zeroed_start_of_week = strip_out_time(start_of_week_for_date_a)
    start_of_next_week = zeroed_start_of_week + timedelta(days=7)
    start_of_week_after = zeroed_start_of_week + timedelta(days=14)
    return start_of_next_week <= date_b < start_of_week_after


def get_week_start_days(start_date: datetime, end_date: datetime):
    """
    Supposing the first week starts on `start_date`, generate the dates that start the weeks subsequent to `start_date`,
    ending with the week that includes `end_date`
    :param start_date: e.g. 2023-04-28 19:15:12
    :param end_date: e.g. 2023-05-17 01:43:57
    :return: e.g. 2023-04-28 00:00:00, 2023-05-05 00:00:00, 2023-05-12 00:00:00
    """
    week_starts = []
    date_cursor = strip_out_time(start_date)  # so that week is counted as starting from 00:00 on whatever provided date
    while date_cursor <= end_date:
        week_starts.append(date_cursor)
        date_cursor += timedelta(days=7)

    return week_starts


def group_performances_per_week(habit):
    """
    Count the number of times a habit was performed each week since a habit was created.  This is more relevant to
    weekly habits.
    :param habit: The habit whose weekly performances we need to group and count
    :return: A list of dictionary objects which each contain a date and a list.  The dates are the start of each week
        since the habit was created, up until the last performance of the habit (NB! only weeks when the habit was
        performed though).  The list contains the habit performances that were done in that week.
    """
    # First week starts the day the habit was created
    date_habit_created = habit.get_created_at()
    # Last week is the one containing the last time the habit was performed (most recent performance)
    most_recent_performance = habit.get_activities()[-1]
    most_recent_performance_date = most_recent_performance.get_performed_at()

    week_starts = get_week_start_days(date_habit_created, most_recent_performance_date)

    activities_per_week = list(map(lambda x: {
        "interval_start": x,
        "activities": None,
    }, week_starts))

    for (idx, week_start) in enumerate(week_starts):
        week_activity_list = activities_per_week[idx]

        def bounded_date_range(x): return week_start <= x.get_performed_at() < week_starts[idx + 1]
        def open_date_range(x): return x.get_performed_at() >= week_start

        week_activity_list["activities"] = list(filter(
            # not at the end of the weeks list yet, so the date range has to be [explicitly] bounded
            bounded_date_range if (idx + 1) < len(week_starts)
            # We are at the end of the weeks list now, so the date range can be "open-ended"
            # (the implicit upper bound is the date when the habit was last performed)
            else open_date_range,
            habit.get_activities()
        ))

    activities_for_active_weeks_only = list(filter(
        lambda x: len(x["activities"]) > 0, activities_per_week
    ))
    activities_for_active_weeks_only.sort(key=lambda y: y["interval_start"])

    return activities_for_active_weeks_only


def group_performances_per_day(habit):
    """
    Given a list of Activity models, group them by the date on which they were performed.
    :param habit: The habit whose activities need to be grouped
    :return: A list of dictionary objects which each contain a date and a list.  The dates are the days on which the
        habit was performed.  The list contains the habit performances that were done on that day.
    """

    all_activities = list(map(
        lambda x: {
            "model": x,
            "performance_date": to_date_string(x.get_performed_at())
        }, habit.get_activities()))

    def group_by_date(grouped, activity):
        curr_date = activity["performance_date"]
        if curr_date not in grouped:
            grouped[curr_date] = []
        grouped[curr_date].append(activity["model"])
        return grouped

    # TODO: Why not use dictionary instead of list??
    # A dictionary where each key is a date string like "2023-12-01" and the value is the list of Activity models
    # for that date (i.e. records of the habit being performed on that day, no matter the time)
    dict_activities_per_day = reduce(group_by_date, all_activities, {})
    # Manipulate the dictionary into list form in order to honour the contract that another similar function is bound to
    list_activities_per_day = list(map(
        lambda activity_date: {
            "interval_start": utils.to_datetime(f"{activity_date} 00:00:00"),
            "activities": dict_activities_per_day[activity_date]
        },
        dict_activities_per_day
    ))

    return list_activities_per_day

