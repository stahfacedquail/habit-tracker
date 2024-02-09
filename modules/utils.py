from uuid import uuid4
from datetime import datetime, timedelta
from typing import Optional
from math import floor
from functools import reduce


def make_uuid():
    """
    Generate a random UUID.
    :return: A stringified UUID
    """
    return str(uuid4())


def to_datetime(datetime_str: str):
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


def add_interval(date_a: str, interval_type: str, num_intervals: int):
    """
    Find the date that is a certain number of days/weeks away from a given date.
    :param date_a: A date-only string, e.g. "2023-10-15"
    :param interval_type: "daily" or "weekly"
    :param num_intervals: The number of days or weeks to add (days/weeks depends on the `interval_type`)
    :return: A date-only string for the date that is `num_intervals` days/weeks away from `date_a`
    """
    dt = to_datetime(f"{date_a} 00:00:00")
    num_days_to_add = (1 if interval_type == "daily" else 7) * num_intervals
    return_dt = dt + timedelta(num_days_to_add)
    return to_date_only_string(return_dt)


def group_activities_by_performance_period(activities: list[object], habit_recurrence: str,
                                           start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """
    Group activities by the day or week in which they were performed.
    :param activities: A list of Activity models for a particular habit.
    :param habit_recurrence: i.e. "daily" or "weekly"
    :param start_date: Only consider activities from this date onwards
    :param end_date: Only consider activities up to and including this date
    :return: A dictionary object where each key is a date-only string and the value is a list of activities.
        * Key: For daily habits, each date is a day on which the habit was performed.  For weekly habits, each date is
        the Monday of a week in which the habit was performed.
        * Value: The list of performances of the habit (Activity models) that occurred in that day/week.
    """
    def make_date_range_fn(start: Optional[datetime], end: Optional[datetime]):
        if start is not None and end is not None:  # both bounds explicitly given
            return lambda x: start <= x.get_performed_at() <= end
        if start is None and end is None:  # no explicit bounds, so let everything through
            return lambda x: True
        if start is None:  # no lower bound, but upper bound defined
            return lambda x: x.get_performed_at() <= end
        if end is None:  # no upper bound, but lower bound is defined
            return lambda x: x.get_performed_at() >= start
    check_date_in_range = make_date_range_fn(start_date, end_date)
    filtered_activities = filter(check_date_in_range, activities)

    augmented_activities = map(
        lambda x: {
            "model": x,
            "performance_period": to_date_only_string(
                x.get_performed_at() if habit_recurrence == "daily"
                else get_week_start_date(x.get_performed_at())
            )
        }, filtered_activities)

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
    :return: A dictionary object containing the accurate start and end dates of the streak, and the length of the streak
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
    }


def get_last_week_date_range(end_date: Optional[datetime] = None):
    if end_date is None:
        end_date = datetime.today()
    start_date = end_date - timedelta(days=6)  # minus 6 and not 7 because range includes today
    return strip_out_time(start_date), end_date


def get_last_month_date_range(end_date: Optional[datetime] = None):
    if end_date is None:
        end_date = datetime.today()

    if end_date.month == 1:
        if end_date.day == 31:  # One month back from 31 Jan must be 1 Jan
            start_date = datetime(end_date.year, 1, 1)
        else:  # One month back from any other date in Jan is the (same date + 1) in December, e.g. one month back from
            # 18 January 2023 is 19 December 2023
            start_date = datetime(end_date.year - 1, 12, end_date.day + 1)
    else:
        try:
            # Try to get (end date + 1) in the previous month...  e.g. if end_date is 15 March 2023, then start_date
            # should be 16 February 2023
            start_date = datetime(end_date.year, end_date.month - 1, end_date.day + 1)
        except ValueError:
            # If it's out of range for previous month, then just begin the range with the 1st day of the end month
            # e.g. If end_date is 30 March 2023, one month before that is "31 February 2023", so just make 1 March 2023
            # the beginning of the range
            start_date = datetime(end_date.year, end_date.month, 1)

    return start_date, end_date


def get_last_6_months_date_range(end_date: Optional[datetime] = None):
    if end_date is None:
        end_date = datetime.today()

    if end_date.month == 6:  # e.g. If end_date is 18 June 2024, start_date should be 19 December 2023
        start_date = datetime(end_date.year - 1, 12, end_date.day + 1)
    elif end_date.month < 6:  # Six months ago will take us to the previous year
        try:
            # e.g. (2 - 6) % 12 == (-4) % 12 == 8, so 6 months back from Feb (month 2) lands us in August (month 8)
            # of the previous year
            start_date = datetime(end_date.year - 1, (end_date.month - 6) % 12, end_date.day + 1)
        except ValueError:
            # If the day is out of range for that month, just start the period at the beginning of the following month
            start_date = datetime(end_date.year - 1, (end_date.month - 6) % 12 + 1, 1)
    else:  # Six months ago lands us within the same year as end_date
        try:
            start_date = datetime(end_date.year, end_date.month - 6, end_date.day + 1)
        except ValueError:
            start_date = datetime(end_date.year, (end_date.month - 6) + 1, 1)

    return start_date, end_date
