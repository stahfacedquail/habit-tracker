import questionary
from typing import Callable

from classes.habit import Habit
from modules.cli.utils import create_choices, perform_habit, close_app

# Stores the function to invoke in order to show the Home menu (avoiding exporting it from original module and causing
# circular imports)
show_home_menu = lambda: None  # noop as initial value


def show_create_habit_menu(show_home_menu_fn: Callable):
    """
    Present the UI to create a new habit
    :param show_home_menu_fn: The function to invoke in order to show the Home menu
    """
    global show_home_menu
    show_home_menu = show_home_menu_fn

    title = None
    while title is None or len(title) == 0:
        title = questionary.text("What is the title of your new habit?").ask()

    recurrence = questionary.select("How often would you like to perform this habit?", create_choices([
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ])).ask()

    new_habit = Habit(title, recurrence)

    questionary.print(f"Your new habit '{new_habit.get_title()}' was successfully created.", style="fg:lime")

    show_create_habit_follow_up_menu(new_habit)


def show_create_habit_follow_up_menu(habit: Habit):
    """
    Post creating a new habit, this menu allows the user to mark it as done for the day/week/etc.
    :param habit: The newly-created habit
    """
    action = questionary.select("What would you like to do next?", create_choices([
        ("perform", f"Mark this habit as done for the {habit.get_interval_label()}"),
        ("home", "Go back home"),
        ("exit", "Exit"),
    ])).ask()

    if action == "perform":
        perform_habit(habit, show_home_menu)
    elif action == "home":
        show_home_menu()
    elif action == "exit":
        close_app()

