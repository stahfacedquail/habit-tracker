from typing import Optional
from datetime import datetime
from modules import db
from classes.habit import Habit


def get_habits(today: Optional[datetime] = None):
    """
    Fetch all the user's habits.
    :return: A list of dictionary objects containing various properties of the user's habits.
    """
    if today is None:  # don't set as default value in constructor because only gets computed once, it seems
        today = datetime.today()

    all_habits = db.get_all_habits()

    def compute_properties(h: dict[str, tuple]):
        habit = Habit(h)

        return {
            "title": habit.get_title(),
            "created_at": habit.get_created_at(),
            "recurrence": habit.get_recurrence(),
            "last_performed": habit.get_date_last_performed(),
            "num_periods_performed": habit.get_number_of_times_completed(end_date=today),
            "completion_rate": round(100 * habit.get_completion_rate(end_date=today)["rate"]),
            "latest_streak": habit.get_latest_streak(today)["length"],
        }

    return list(map(compute_properties, all_habits))


def sort_habits(habits: list[dict], sort_field: str, order: str):
    """
    Sort the list of habit tuples.
    :param habits: A list of tuples each containing details about a habit
    :param sort_field: The property by which to sort the list, e.g. "completion_rate"
    :param order: "asc" or "desc", i.e. whether to sort by ascending or descending order
    :return: A new list of habit dictionary objects, sorted as requested
    """
    def sort_with_none_type(h):
        val = h[sort_field]
        if sort_field == "last_performed":
            if val is None:
                return datetime.fromtimestamp(0)  # make it behave like the earliest value the date could be

        if isinstance(val, str):  # case-insensitive sorting for string fields
            return val.lower()

        return val

    return sorted(habits, key=sort_with_none_type, reverse=(order == "desc"))


def filter_habits(habits: list[dict], prop: str, value: any):
    """
    Show a subset of the list of habit dictionary objects, filtered by a particular property.
    :param habits: A list of dictionary objects each containing details about a habit
    :param prop: The property by which to filter the list.  Currently only available property is "recurrence".
    :param value: Only display habits whose value for the requested `prop` is `value`
    :return: A new list of habit dictionary objects, filtered as requested
    """
    return list(filter(lambda h: h[prop] == value, habits))
