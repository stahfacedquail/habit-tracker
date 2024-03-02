import sys

import questionary
from typing import Optional, Callable
from tabulate import tabulate

from modules import habits
from modules.utils import get_last_month_date_range, get_last_week_date_range, get_last_6_months_date_range
from classes.habit import Habit
from modules.cli.utils import create_choices, get_latest_streak_message, perform_habit, get_custom_date_range

# Stores the function to invoke in order to show the Home menu (avoiding exporting it from original module and causing
# circular imports)
show_home_menu = lambda: None  # noop as initial value


def show_habits_abridged(show_home_menu_fn: Optional[Callable] = None):
    """
    Show a list of the habits' titles for the user to select from, in order for them to execute some action on that
    habit
    :param show_home_menu_fn: The function to invoke in order to show the Home menu
    """
    global show_home_menu
    if show_home_menu_fn is not None:
        show_home_menu = show_home_menu_fn

    habits_list = habits.get_habits_abridged()
    action = questionary.select("Which habit would you like to look at?", create_choices(habits_list + [
        ("home", "Go back home"),
        ("exit", "Exit"),
    ])).ask()

    if action == "home":
        show_home_menu()
    elif action == "exit":
        sys.exit()
    else:
        habit_uuid = action
        habit = Habit(habit_uuid)
        show_habit_actions_menu(habit)


def show_habit_actions_menu(habit: Habit):
    """
    Show a menu with the actions that can be executed on a given habit
    :param habit: The habit that the user wants to see details of or mark as done etc.
    """
    latest_streak = habit.get_latest_streak()
    streak_message = get_latest_streak_message(latest_streak, habit.get_recurrence())

    last_performed = habit.get_date_last_performed()
    questionary.print(f"""
Title: {habit.get_title()}
Date created: {habit.get_created_at()}
Recurrence: {habit.get_recurrence()}
Last performed: {last_performed if last_performed is not None else "No activities recorded yet"}
Latest streak: {streak_message}
    """)

    action = questionary.select("What would you like to do next?", create_choices([
        ("perform", f"Mark this habit as done for the {habit.get_interval_label()}"),
        ("streaks", "View all the streaks for this habit"),
        ("completion", "View your completion rate for this habit"),
        ("delete", "Delete this habit"),
        ("back", "Go back to the list of all your habits"),
        ("exit", "Exit"),
    ])).ask()

    if action == "perform":
        perform_habit(habit, show_habits_abridged)
    elif action == "streaks":
        show_streaks_menu(habit)
    elif action == "completion":
        show_completion_rate_menu(habit)
    elif action == "delete":
        show_delete_habit_menu(habit)
    elif action == "back":
        show_habits_abridged()
    elif action == "exit":
        sys.exit()


def show_streaks_menu(habit: Habit):
    """
    Show the user the streaks they have achieved for a given habit, with the options to sort the streaks
    :param habit: The habit whose streaks will be shown
    """
    sort_field = questionary.select("Sort the streaks by:", create_choices([
        ("date", "when they started"),
        ("length", "length"),
    ])).ask()

    sort_order = questionary.select("Start from:", create_choices([
        ("asc", "the oldest streak" if sort_field == "date" else "the shortest streak"),
        ("desc", "the latest streak" if sort_field == "date" else "the longest streak")
    ])).ask()

    streaks = habit.get_all_streaks(sort_field, sort_order)
    if len(streaks) == 0:
        questionary.print("You haven't achieved any streaks yet 🥺")
    else:
        streaks_table = list(map(lambda streak: [
            streak["length"],
            streak["start"],
            streak["end"],
        ], streaks))
        print(tabulate(streaks_table,
                       headers=[f"Length ({habit.get_interval_label()}s)", "From", "Until"],
                       colalign=("center",)))

    follow_up_action = questionary.select("What would you like to do next?", create_choices([
        ("change_sort", "Choose a different order to sort the streaks"),
        ("habit_details", "Show the details of the habit"),
        ("exit", "Exit"),
    ])).ask()

    if follow_up_action == "change_sort":
        show_streaks_menu(habit)
    elif follow_up_action == "habit_details":
        show_habit_actions_menu(habit)
    elif follow_up_action == "exit":
        sys.exit()


def show_completion_rate_menu(habit: Habit):
    """
    Show the user how successfully they completed a given habit over a certain period.
    :param habit: The habit whose completion rate the user wants to see
    """
    date_ranges = create_choices([
        ("last_wk", "Past 7 days"),
        ("last_mo", "Last month"),
        ("custom", "Custom"),
     ]) if habit.get_recurrence() == "daily" else create_choices([
        ("last_mo", "Last month"),
        ("last_6_mo", "Last 6 months"),
        ("custom", "Custom"),
    ])

    date_range_choice = questionary.select("Which date range would you like to see your completion rate for?",
                                           date_ranges).ask()

    if date_range_choice == "custom":
        (start_date, end_date) = get_custom_date_range()
    else:
        if date_range_choice == "last_wk":
            (start_date, end_date) = get_last_week_date_range()
        elif date_range_choice == "last_mo":
            (start_date, end_date) = get_last_month_date_range()
        else:
            (start_date, end_date) = get_last_6_months_date_range()

    # Cap the date range so that it does not go beyond the date when the habit was created
    start_date = max(start_date, habit.get_created_at())
    completion = habit.get_completion_rate(start_date, end_date)

    completion_message_intro = f"From {start_date} to {end_date},"
    completion_message = f"you have performed this habit on {completion['num_active_periods']} out of " +\
        f"{completion['num_total_periods']} {habit.get_interval_label(completion['num_total_periods'])}.\n" +\
        f"This is a completion rate of {round(100 * completion['rate'])}%."
    questionary.print(f"{completion_message_intro} {completion_message}")

    follow_up_action = questionary.select("What would you like to do next?", create_choices([
        ("different_date_range", "View your completion rate over a different date range"),
        ("habit_details", "Show all the details of this habit"),
        ("exit", "Exit"),
    ])).ask()

    if follow_up_action == "different_date_range":
        show_completion_rate_menu(habit)
    elif follow_up_action == "habit_details":
        show_habit_actions_menu(habit)
    elif follow_up_action == "exit":
        sys.exit()


def show_delete_habit_menu(habit: Habit):
    """
    Display the UI for the user to delete a given habit.
    :param habit: The habit the user wants to delete
    """
    confirm_delete = questionary.confirm("Are you sure you want to delete this habit?").ask()
    if confirm_delete:
        habit.remove()
        questionary.print("The habit was successfully deleted.", style="fg:lime")

        follow_up_action = questionary.select("What would you like to do next?", create_choices([
            ("habits_list", "Go back to the list of all your habits"),
            ("home", "Go back home"),
            ("exit", "Exit"),
        ])).ask()

        if follow_up_action == "home":
            show_home_menu()
        elif follow_up_action == "habits_list":
            show_habits_abridged(show_home_menu)
        elif follow_up_action == "exit":
            sys.exit()
    else:
        show_habit_actions_menu(habit)
