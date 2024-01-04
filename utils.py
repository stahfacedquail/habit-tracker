from uuid import uuid4
from datetime import datetime, timedelta


def make_uuid():
    return str(uuid4())


def to_datetime(datetime_str):
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def strip_out_time(dt: datetime):
    return datetime(year=dt.year, month=dt.month, day=dt.day)


def get_num_days_from_to(start_date: datetime, end_date: datetime):
    start_date_ignoring_time = strip_out_time(start_date)
    end_date_ignoring_time = strip_out_time(end_date)
    return (end_date_ignoring_time - start_date_ignoring_time).days + 1


def get_num_weeks_from_to(start_of_begin_week: datetime, start_of_end_week: datetime):
    start_date_ignoring_time = strip_out_time(start_of_begin_week)
    end_date_ignoring_time = strip_out_time(start_of_end_week)
    return (end_date_ignoring_time - start_date_ignoring_time)/7 + 1


def is_next_day(date_a: datetime, date_b: datetime):
    next_day = strip_out_time(date_a) + timedelta(days=1)
    return strip_out_time(date_b) == next_day


def is_next_week(start_of_week_for_date_a: datetime, date_b: datetime):
    zeroed_start_of_week = strip_out_time(start_of_week_for_date_a)
    start_of_next_week = zeroed_start_of_week + timedelta(days=7)
    start_of_week_after = zeroed_start_of_week + timedelta(days=14)
    return start_of_next_week <= date_b < start_of_week_after


def get_week_start_days(start_date: datetime, end_date: datetime):
    week_starts = []
    date_cursor = strip_out_time(start_date)  # so that week is counted as starting from 00:00 on whatever provided date
    while date_cursor <= end_date:
        week_starts.push(date_cursor)
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
    most_recent_performance = habit.get_activities()[0]
    most_recent_performance_date = most_recent_performance.get_performed_at()

    week_starts = get_week_start_days(date_habit_created, most_recent_performance_date)

    activities_per_week = map(lambda x: {
        "interval_start": x,
        "activities": None,
    }, week_starts)

    for (idx, week_start) in enumerate(week_starts):
        week_activity_list = activities_per_week[idx]

        def bounded_date_range(x): return week_start <= x.get_performed_at() < week_start[idx + 1]
        def open_date_range(x): return x.get_performed_at() >= week_start

        week_activity_list["activities"] = list(filter(
            # not at the end of the weeks list yet, so the date range has to be [explicitly] bounded
            bounded_date_range if (idx + 1) < len(week_starts)
            # We are at the end of the weeks list now, so the date range can be "open-ended"
            # (the implicit upper bound is the date when the habit was last performed)
            else open_date_range,
            habit.get_activities()
        ))

    return list(filter(
        lambda x: len(x["activities"]) > 0, activities_per_week
    )).sort(lambda y: y["interval_start"])


def group_performances_per_day(habit):
    active_days = list(set(map(
        lambda x: strip_out_time(x.get_performed_at()), habit.get_activities()
    )))
    active_days.sort()
    activities_per_day = []

    for day_start in active_days:
        next_day_start = day_start + timedelta(days=1)
        activities_on_this_day = list(filter(
            lambda x: day_start <= x.get_performed_at() < next_day_start,
            habit.get_activities()
        ))

        activities_per_day.append({
            "interval_start": day_start,
            "activities": activities_on_this_day,
        })

    return activities_per_day
