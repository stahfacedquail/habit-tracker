import questionary

from modules.cli.utils import create_choices, close_app, print_menu_title, print_greeting
from modules.cli.create_habit import show_create_habit_menu
from modules.cli.view_habit_detail import show_habits_abridged
from modules.cli.view_stats import show_stats_menu


def show_home_menu(starting_up=False):
    """
    Shows the home menu containing the basic paths a user can take in this application
    :param starting_up: Indicates whether this is the very first home menu being shown
    """
    if starting_up:
        print_greeting("Welcome to your habit tracker!")
        questionary.print("")

    print_menu_title("Home")
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
        close_app()
