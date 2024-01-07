from uuid import uuid4
from datetime import datetime, timedelta
from math import floor
from functools import reduce


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


def get_num_days_from_to(start_date: datetime, end_date: datetime, inclusive: bool = True):
    """
    Count the number of days from `start_date` up to (and maybe including) `end_date`.
    :param start_date: e.g. 2023-12-25 12:00:21
    :param end_date: e.g. 2024-01-12 08:12:12
    :param inclusive: Should `end_date` be included?
    :return: e.g. 19
    """
    start_date_ignoring_time = strip_out_time(start_date)
    end_date_ignoring_time = strip_out_time(end_date)
    return (end_date_ignoring_time - start_date_ignoring_time).days + (1 if inclusive else 0)


def get_num_weeks_from_to(date_a: datetime, date_b: datetime):
    """
    Count the number of weeks that contain the date range from `date_a` to `date_b` (where a subset of the Monday-to-
    Sunday week counts as 1 week).
    :param date_a: e.g. 2023-12-27 12:00:21 (a Wednesday)
    :param date_b: e.g. 2024-01-08 08:12:12 (a Monday, about 2 weeks later)
    :return: 3
    """
    monday_for_start_date = strip_out_time(date_a - timedelta(days=date_a.weekday()))
    monday_for_end_date = strip_out_time(date_b - timedelta(days=date_b.weekday()))
    return floor((monday_for_end_date - monday_for_start_date).days/7) + 1


def get_week_start_date(date_a: datetime):
    """
    Given `date_a`, return the date of the Monday that begins the week containing `date_a`.
    :param date_a: e.g. 12 December 2023 (is on a Tuesday)
    :return: 11 December 2023 (the Monday that begins the week containing 12 December 2023)
    """
    return strip_out_time(date_a) - timedelta(date_a.weekday())


def group_activities_by_performance_period(activities: list[object], habit_recurrence: str):
    """
    Group activities by the day or week in which they were performed.
    :param activities: A list of Activity models for a particular habit.
    :param habit_recurrence: i.e. "daily" or "weekly"
    :return: A dictionary object where each key is a date-only string and the value is a list of activities.
        * Key: For daily habits, each date is a day on which the habit was performed.  For weekly habits, each date is
        the Monday of a week in which the habit was performed.
        * Value: The list of performances of the habit (Activity models) that occurred in that day/week.
    """
    augmented_activities = list(map(
        lambda x: {
            "model": x,
            "performance_period": to_date_only_string(
                x.get_performed_at() if habit_recurrence == "daily"
                else get_week_start_date(x.get_performed_at())
            )
        }, activities))

    def group_by_date(grouped, activity):
        curr_date = activity["performance_period"]
        if curr_date not in grouped:
            grouped[curr_date] = []
        grouped[curr_date].append(activity["model"])
        return grouped

    return reduce(group_by_date, augmented_activities, {})


def get_streak_accurate_params(start_date_activities: str, end_date_activities: str, habit: object):
    """
    Given the activities from the streak's start date and the activities from the streak's end date, figure out the
    earliest activity in the first batch and the latest activity in the latter; these are the accurate beginning and
    ending dates of the streak.
    :param start_date_activities: A date-only string, e.g. "2023-01-24"
    :param end_date_activities: A date-only string, e.g. "2023-01-31"
    :param habit: The Habit model to whom the activities belong
    :return: A dictionary object containing the accurate start and end dates of the streak, the length of the streak,
        and the unit of measurement for the streak based on the habit's recurrence type (i.e. either "days" or "weeks").
    """
    first_activity = sorted(start_date_activities, key=lambda activity: activity.get_performed_at())[0]
    last_activity = sorted(end_date_activities, key=lambda activity: activity.get_performed_at())[-1]

    accurate_start = first_activity.get_performed_at()
    accurate_end = last_activity.get_performed_at()
    length = get_num_days_from_to(accurate_start, accurate_end) if habit.get_recurrence() == "daily" \
        else get_num_weeks_from_to(accurate_start, accurate_end)
    return {
        "start": accurate_start,
        "end": accurate_end,
        "length": length,
        "unit": habit.get_streak_unit()
    }
