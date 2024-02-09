import sys

import questionary

from modules.cli.utils import create_choices
from modules.cli.create_habit import show_create_habit_menu
from modules.cli.view_habit_detail import show_habits_abridged
from modules.cli.view_stats import show_stats_menu


# TODO: Pause between actions to let user first digest outcome, and then choose next action
# TODO: Format dates nicely e.g. 23 December 2023
# TODO: Instead of just sys.exit, show a nice goodbye message then exit
# TODO: Headings to show where in the program the user is
# TODO: Display for correct timezone
# TODO: Alignment in tables (especially stats one) -- field-dependent

def show_home_menu(starting_up=False):
    """
    Shows the home menu containing the basic paths a user can take in this application
    :param starting_up: Indicates whether this is the very first home menu being shown
    """
    if starting_up:
        questionary.print("Welcome to your habit tracker!")

    action = questionary.select("What would you like to do?", create_choices([
        ("create", "Create a new habit"),
        ("show_one", "View one habit"),
        ("stats", "Look at the stats for all your habits"),
        ("exit", "Exit"),
    ])).ask()

    if action == "create":
        show_create_habit_menu(show_home_menu)
    elif action == "show_one":
        show_habits_abridged(show_home_menu)
    elif action == "stats":
        show_stats_menu(show_home_menu)
    elif action == "exit":
        sys.exit()
