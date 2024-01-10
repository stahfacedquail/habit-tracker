from typing import Optional
import db
from classes.habit import Habit


def get_habits():
    """
    Fetch all the user's habits.
    :return: A list of tuples containing various properties of the user's habits.
    """
    all_habits = db.get_all_habits()

    def compute_properties(habit_tuple: tuple):
        habit = Habit(habit_tuple)
        return {
            "title": habit.get_title(),
            "created_at": habit.get_created_at(),
            "recurrence": habit.get_recurrence(),
            "last_performed": habit.get_date_last_performed(),
            "num_periods_performed": habit.get_number_of_times_completed(),
            "completion_rate": habit.get_completion_rate(),
            "current_streak": habit.get_latest_streak(),
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
    :return: A new list of habit tuples, sorted as requested
    """
    if secondary_prop is None:
        return sorted(habits, key=lambda h: h[primary_prop], reverse=(order == "desc"))
    else:
        return sorted(habits, key=lambda h: h[primary_prop][secondary_prop], reverse=(order == "desc"))


def filter_habits(habits: list[tuple], prop: str, value: any):
    """
    Show a subset of the list of habit tuples, filtered by a particular property.
    :param habits: A list of tuples each containing details about a habit
    :param prop: The property by which to filter the list.  Currently only available property is "recurrence_type".
    :param value: Only display habits whose value for the requested `prop` is `value`
    :return: A new list of habit tuples, filtered as requested
    """
    return list(filter(lambda h: h[prop] == value, habits))
