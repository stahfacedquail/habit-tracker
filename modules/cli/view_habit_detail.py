import questionary
from typing import Optional, Callable
from tabulate import tabulate
from datetime import datetime

from modules.utils import get_last_month_date_range, get_last_week_date_range, get_last_6_months_date_range, \
    prettify_datetime, get_start_of_day, get_end_of_day
from classes.habit import Habit
from modules.cli.utils import create_choices, get_latest_streak_message, perform_habit, get_custom_date_range,  \
    close_app, print_menu_title, print_success_message

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

    print_menu_title("Your habits")
    habits_list = Habit.get_all_abridged()
    action = questionary.select("Which habit would you like to look at?", create_choices(habits_list + [
        ("home", "Go back home"),
        ("exit", "Exit"),
    ])).ask()

    if action == "home":
        show_home_menu()
    elif action == "exit":
        close_app()
    else:
        habit_uuid = action
        habit = Habit(habit_uuid)
        show_habit_actions_menu(habit)


def show_habit_actions_menu(habit: Habit):
    """
    Show a menu with the actions that can be executed on a given habit
    :param habit: The habit that the user wants to see details of or mark as done etc.
    """
    print_menu_title(f"Habit: {habit.get_title()}")

    latest_streak = habit.get_latest_streak()
    streak_message = get_latest_streak_message(latest_streak, habit.get_recurrence())

    last_performed = habit.get_date_last_performed()
    questionary.print(
        f"""Title: {habit.get_title()}
Date created: {prettify_datetime(habit.get_created_at(), True)}
Recurrence: {habit.get_recurrence()}
Last performed: {prettify_datetime(last_performed, True)
                 if last_performed is not None
                 else "No activities recorded yet"}
Latest streak: {streak_message}
""")
    questionary.press_any_key_to_continue().ask()

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
        close_app()


def show_streaks_menu(habit: Habit):
    """
    Show the user the streaks they have achieved for a given habit, with the options to sort the streaks
    :param habit: The habit whose streaks will be shown
    """
    print_menu_title(f"Streaks for '{habit.get_title()}'")

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
        questionary.print("Sorry for all that hassle, but you haven't achieved any streaks yet 🥺")
    else:
        streaks_table = list(map(lambda streak: [
            streak["length"],
            prettify_datetime(streak["start"]),
            prettify_datetime(streak["end"]),
        ], streaks))
        print(tabulate(streaks_table,
                       headers=[f"Length ({habit.get_interval_label()}s)", "From", "Until"],
                       colalign=("center",)))

    questionary.press_any_key_to_continue().ask()

    follow_up_action = questionary.select("What would you like to do next?", create_choices([
        ("change_sort", "Choose a different order to sort the streaks"),
        ("habit_details", "Go back to the details of this habit"),
        ("exit", "Exit"),
    ])).ask()

    if follow_up_action == "change_sort":
        show_streaks_menu(habit)
    elif follow_up_action == "habit_details":
        show_habit_actions_menu(habit)
    elif follow_up_action == "exit":
        close_app()


def show_completion_rate_menu(habit: Habit):
    """
    Show the user how successfully they completed a given habit over a certain period.
    :param habit: The habit whose completion rate the user wants to see
    """
    print_menu_title(f"Completion rate for '{habit.get_title()}'")

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

    start_date_too_early = start_date < get_start_of_day(habit.get_created_at())
    end_date_too_late = end_date > get_end_of_day(datetime.today())
    if start_date_too_early or end_date_too_late:
        if start_date_too_early and end_date_too_late:
            questionary.print(f"Note that this habit was created on {prettify_datetime(habit.get_created_at())},"
                              " and the date range that you've chosen starts before that." +
                              f"  Additionally, the date today is {prettify_datetime(datetime.today())}," +
                              " and the date range that you've chosen ends after that." +
                              "  As a result, the completion rate you will see might be lower than how you have" +
                              " actually performed up to today.")
        elif start_date_too_early:
            questionary.print(f"Note that this habit was created on {prettify_datetime(habit.get_created_at())}," +
                              " and the date range that you've chosen starts before that." +
                              "  As a result, the completion rate you will see might be lower than how you have" +
                              " actually performed since you started recording this habit.")
        else:  # end_date_too_late is True
            questionary.print(f"Note that the date today is {prettify_datetime(datetime.today())}," +
                              " and the date range that you've chosen ends after that." +
                              "  As a result, the completion rate you will see might be lower than how you have" +
                              " actually performed up to today.")

        questionary.press_any_key_to_continue().ask()

    completion = habit.get_completion_rate(start_date, end_date)
    completion_message_intro = f"From {prettify_datetime(start_date, False)} to {prettify_datetime(end_date)},"
    completion_message = f"you have performed this habit on {completion['num_active_periods']} out of " + \
                         f"{completion['num_total_periods']} {habit.get_interval_label(completion['num_total_periods'])}.\n" + \
                         f"This is a completion rate of {round(100 * completion['rate'])}%."
    questionary.print(f"{completion_message_intro} {completion_message}")

    questionary.press_any_key_to_continue().ask()

    follow_up_action = questionary.select("What would you like to do next?", create_choices([
        ("different_date_range", "View your completion rate over a different date range"),
        ("habit_details", "Go back to the details of this habit"),
        ("exit", "Exit"),
    ])).ask()

    if follow_up_action == "different_date_range":
        show_completion_rate_menu(habit)
    elif follow_up_action == "habit_details":
        show_habit_actions_menu(habit)
    elif follow_up_action == "exit":
        close_app()


def show_delete_habit_menu(habit: Habit):
    """
    Display the UI for the user to delete a given habit.
    :param habit: The habit the user wants to delete
    """
    print(f"Delete '{habit.get_title()}'")

    confirm_delete = questionary.confirm("Are you sure you want to delete this habit?").ask()
    if confirm_delete:
        habit.remove()
        print_success_message("The habit was successfully deleted.")

        questionary.press_any_key_to_continue().ask()

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
            close_app()
    else:
        show_habit_actions_menu(habit)
