from typing import Optional
from datetime import datetime
import db
from classes.habit import Habit


def get_habits(today: Optional[datetime] = datetime.today()):
    """
    Fetch all the user's habits.
    :return: A list of dictionary objects containing various properties of the user's habits.
    """
    all_habits = db.get_all_habits()

    def compute_properties(h: dict[str, tuple]):
        habit = Habit(h)
        return {
            "title": habit.get_title(),
            "created_at": habit.get_created_at(),
            "recurrence": habit.get_recurrence(),
            "last_performed": habit.get_date_last_performed(),
            "num_periods_performed": habit.get_number_of_times_completed(end_date=today),
            "completion_rate": habit.get_completion_rate(end_date=today),
            "latest_streak": habit.get_latest_streak(today),
        }

    return list(map(compute_properties, all_habits))


def sort_habits(habits: list[dict], order: str, primary_prop: str, secondary_prop: Optional[str] = None):
    """
    Sort the list of habit tuples.
    :param habits: A list of tuples each containing details about a habit
    :param primary_prop: The property by which to sort the list, e.g. "completion_rate"
    :param secondary_prop: Sometimes there is more than one way to sort on `primary_prop`, e.g. for "current_streak",
        one can sort by length of the streak or by date.
    :param order: "asc" or "desc", i.e. whether to sort by ascending or descending order
    :return: A new list of habit dictionary objects, sorted as requested
    """
    def sort_with_none_type(h):
        val = h[primary_prop] if secondary_prop is None else h[primary_prop][secondary_prop]
        if primary_prop == "last_performed" or (primary_prop == "latest_streak" and
                                            (secondary_prop in ["start", "end", "is_current", "can_extend_today"])):
            if val is None:
                return datetime.fromtimestamp(0)  # make it behave like the earliest value the date could be

        return val

    return sorted(habits, key=sort_with_none_type, reverse=(order == "desc"))


def filter_habits(habits: list[tuple], prop: str, value: any):
    """
    Show a subset of the list of habit tuples, filtered by a particular property.
    :param habits: A list of tuples each containing details about a habit
    :param prop: The property by which to filter the list.  Currently only available property is "recurrence_type".
    :param value: Only display habits whose value for the requested `prop` is `value`
    :return: A new list of habit dictionary objects, filtered as requested
    """
    return list(filter(lambda h: h[prop] == value, habits))
