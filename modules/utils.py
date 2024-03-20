from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Optional
from math import floor
from functools import reduce


def make_uuid():
    """
    Generate a random UUID.
    :return: A stringified UUID
    """
    return str(uuid4())


def get_as_local_time(dt_as_gmt: datetime):
    """
    Converts a GMT datetime to a datetime in the local timezone
    :param dt_as_gmt: GMT datetime object
    :return: Datetime object with local time
    """
    return datetime.fromtimestamp(dt_as_gmt.timestamp())


def get_as_gmt(local_dt: datetime):
    """
    Converts a datetime into its GMT equivalent
    :param local_dt: The datetime in a local timezone
    :return: The GMT equivalent of `local_dt`
    """
    return datetime.fromtimestamp(local_dt.timestamp(), tz=timezone.utc)


def format_date_for_db(dt_string: str):
    """
    Turns the provided datetime string into a GMT datetime string in the correct format for the database
    :param dt_string: A datetime string that is naive (assumes the local timezone)
    :return: A GMT datetime string that looks like 2023-01-20 00:57:12
    """
    return datetime.strftime(       # (3) format correctly for db
        get_as_gmt(                 # (2) turn into GMT datetime object
            to_datetime(dt_string)  # (1) turn into naive datetime object (assumes local timezone)
        ), "%Y-%m-%d %H:%M:%S")


def to_datetime(datetime_str: str, is_gmt: bool = False):
    """
    Take a date/time string and convert into a naive datetime object
    :param datetime_str: e.g. "2023-10-05 12:00:54", which is how dates are stored in the database
    :param is_gmt: Indicates whether `datetime_str` is a GMT datetime (otherwise assumption is that
        it is a local time)
    :return: The corresponding datetime object (local timezone)
    """
    if is_gmt:
        gmt_dt = datetime.strptime(f"{datetime_str}+0000", "%Y-%m-%d %H:%M:%S%z")
        return get_as_local_time(gmt_dt)

    return datetime.strptime(f"{datetime_str}", "%Y-%m-%d %H:%M:%S")


def to_date_only_string(dt: datetime):
    """
    Get a date-only string from `dt`, a datetime object.
    :param dt: A datetime object in the local timezone
    :return: A date-only string like "2023-10-05" (local timezone)
    """
    return dt.strftime("%Y-%m-%d")


def prettify_datetime(dt: datetime, with_time=True):
    """
    Get a prettified string of the given datetime object
    :param dt: A datetime object (local time)
    :param with_time: A boolean indicating whether to include the time or not
    :return: A datetime string like "23 December 2023, 13:08" (local time)
    """
    if with_time:
        return dt.strftime("%-d %B %Y, %H:%M")

    return dt.strftime("%-d %B %Y")

def get_start_of_day(dt: datetime):
    """
    :param dt: A datetime object (local time)
    :return: A new datetime object where the time on that date is midnight (local time)
    """
    return datetime(dt.year, dt.month, dt.day)


def get_num_days_from_to(start_date: datetime, end_date: datetime, inclusive: bool = True):
    """
    Count the number of days from `start_date` up to (and maybe including) `end_date`.
    :param start_date: e.g. 2023-12-25 12:00:21
    :param end_date: e.g. 2024-01-12 08:12:12
    :param inclusive: Should `end_date` be included?
    :return: e.g. 19
    """
    start_date_ignoring_time = get_start_of_day(start_date)
    end_date_ignoring_time = get_start_of_day(end_date)
    return (end_date_ignoring_time - start_date_ignoring_time).days + (1 if inclusive else 0)


def get_num_weeks_from_to(date_a: datetime, date_b: datetime):
    """
    Count the number of weeks that contain the date range from `date_a` to `date_b` (where a subset of the Monday-to-
    Sunday week counts as 1 week).
    :param date_a: e.g. 2023-12-27 12:00:21 (a Wednesday)
    :param date_b: e.g. 2024-01-08 08:12:12 (a Monday, about 2 weeks later)
    :return: 3
    """
    monday_for_start_date = get_start_of_day(date_a - timedelta(days=date_a.weekday()))
    monday_for_end_date = get_start_of_day(date_b - timedelta(days=date_b.weekday()))
    return floor((monday_for_end_date - monday_for_start_date).days/7) + 1


def get_week_start_date(date_a: datetime):
    """
    Given `date_a`, return the date of the Monday that begins the week containing `date_a`.
    :param date_a: e.g. 12 December 2023 14:30:00 (is on a Tuesday) (local time)
    :return: e.g. 11 December 2023 00:00:00 (the Monday that begins the week containing 12 December 2023) (local time)
    """
    return get_start_of_day(date_a) - timedelta(date_a.weekday())


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
    :param start_date: Only consider activities from this date onwards (local time)
    :param end_date: Only consider activities up to and including this date (local time)
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
        lambda x: dict({
            "model": x,
            "performance_period": to_date_only_string(
                x.get_performed_at() if habit_recurrence == "daily"
                else get_week_start_date(x.get_performed_at())
            )
        }), filtered_activities)

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
    """
    Get the date range that spans the last 7 days.  Note that we do not mean a technical 7 days (i.e. 7 * 24 hours), but
    rather 7 semantic days, e.g. if `end_date` is a Thursday, "7 days" goes from midnight the previous Friday until the
    time of the provided `end_date`.  If no `end_date` is provided, the current time is taken to be the `end_date`.
    :param end_date: The end of the 7-day range
    :return: A tuple with two datetime objects (local time): the start and end of the 7-day range
    """
    if end_date is None:
        end_date = datetime.today()
    start_date = end_date - timedelta(days=6)  # minus 6 and not 7 because range includes today
    return get_start_of_day(start_date), end_date


def get_last_month_date_range(end_date: Optional[datetime] = None):
    """
    Get the date range that spans the last month.  Note that by a month, supposing `end_date` is 12 July 2023, the month
    range would run from 13 June 2023 until 12 July 2023.  If the date has no such a "partner" in the previous month
    (e.g. if `end_date` is 31 March 2023, the start_date naively would have to be 32 February 2023), we use the 1st of
    that month as the start of the month range (in the example, the start would be 1 March 2023 instead).  If no
    `end_date` is provided, the current time is taken to be the `end_date`.
    :param end_date: The end of the month range
    :return: A tuple with two datetime objects (local time): the start and end of the month range
    """
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
    """
    Get the date range that spans the last 6 months.  Note that by 6 months, supposing `end_date` is 12 July 2023, the
    6-month range would run from 13 January 2023 until 12 July 2023.  If the date has no such a "partner" in the
    starting month (e.g. if `end_date` is 28 August 2023, the start_date naively would have to be 29 February 2023), we
    use the 1st of the next month as the start of the 6-month range (in the example, the start would be 1 March 2023
    instead).  If no `end_date` is provided, the current time is taken to be the `end_date`.
    :param end_date: The end of the 6-month range
    :return: A tuple with two datetime objects (local time): the start and end of the 6-month range
    """
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
