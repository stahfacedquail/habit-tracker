import sys
from datetime import datetime, timedelta
from typing import Optional
from functools import reduce

import questionary
from tabulate import tabulate

import analytics
import db
import utils
from classes.habit import Habit
from modules import habits


def create_choices(options: list[tuple]):
    return list(map(lambda opt: questionary.Choice(value=opt[0], title=opt[1]), options))


def show_home_menu(starting_up = False):
    if starting_up:
        questionary.print("Welcome to your habit tracker!")

    action = questionary.select("What would you like to do?", create_choices([
        ("create", "Create a new habit"),
        ("show_one", "View one habit"),
        ("stats", "Look at the stats for all your habits"),
        ("exit", "Exit"),
    ])).ask()

    if action == "create":
        show_create_habit_menu()
    elif action == "show_one":
        show_habits_abridged()
    elif action == "stats":
        show_stats_menu()
    elif action == "exit":
        sys.exit()


def show_create_habit_menu(follow_up: Optional[any] = None):
    title = None
    while title is None or len(title) == 0:
        title = questionary.text("What is the title of your new habit?").ask()

    recurrence = questionary.select("How often would you like to perform this habit?", create_choices([
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ])).ask()

    # TODO: Wrap in try/catch; show error menu in catch
    new_habit = Habit(title, recurrence)

    questionary.print(f"Your new habit '{new_habit.get_title()}' was successfully created.", style="fg:lime")

    if follow_up is not None:
        follow_up()
    else:
        show_create_habit_follow_up_menu(new_habit)


def show_create_habit_follow_up_menu(habit: Habit):
    interval = "day" if habit.get_recurrence() == "daily" else "week"

    action = questionary.select("What would you like to do next?", create_choices([
        ("perform", f"Mark this habit as done for the {interval}"),
        ("home", "Go back home"),
        ("exit", "Exit"),
    ])).ask()

    if action == "perform":
        perform_habit(habit)
    elif action == "home":
        show_home_menu()
    elif action == "exit":
        sys.exit()


def perform_habit(habit: Habit, next_menu: Optional[any] = None):
    habit.perform()
    interval = "day" if habit.get_recurrence() == "daily" else "week"
    questionary.print(f"You've marked the habit '{habit.get_title()}' as done for the {interval}; nice!",
                      style="fg:lime")
    if next_menu is not None:
        next_menu()
    else:
        show_home_menu()


def show_habits_abridged():
    habits_list = habits.get_habits_abridged()
    habits_list.extend([
        ("home", "Go back home"),
        ("exit", "Exit"),
    ])
    action = questionary.select("Which habit would you like to look at?", create_choices(habits_list)).ask()

    if action == "home":
        show_home_menu()
    elif action == "exit":
        sys.exit()
    else:
        habit = Habit(action)
        show_habit_actions_menu(habit)


def get_latest_streak_message(streak: dict, recurrence: str):
    if streak["start"] is None:
        return "You haven't had any streaks yet, so today feels like a good day to kick one off 🚀"

    if streak["is_current"] is False:
        part_1 = f"Your last streak ran from {streak['start']} until {streak['end']}"
        part_2 = f"— a {'decent' if streak['length'] <= 4 else 'whopping'}"
        part_3 = f"{streak['length']} {streak['unit']}!"
        part_4 = "Today feels like a good day to start a new one 🚀"

        return f"{part_1} {part_2} {part_3}  {part_4}"

    part_1 = "You are currently on a roll!"
    part_2 = f"You've kept up this habit for {streak['length']} {streak['unit']} 🥳"

    if streak["can_extend_today"] is False:
        part_3 = f"Remember to perform this habit again {'tomorrow' if recurrence == 'daily' else 'next week'}."
    else:
        part_3 = f"To maintain your streak, be sure to perform this habit again before the end of {
            'today' if recurrence == 'daily' else 'this week'}."

    return f"{part_1}  {part_2}  {part_3}"


def show_habit_actions_menu(habit: Habit):
    # TODO Format dates nicely e.g. 23 December 2023
    # TODO Tabs to align
    # TODO "1 days" vs "1 day"
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
        ("perform", f"Mark this habit as done for the {'day' if habit.get_recurrence() == 'daily' else 'week'}"),
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
    sort_field = questionary.select("Sort the streaks by:", create_choices([
        ("date", "when they started"),
        ("length", "length"),
    ])).ask()

    sort_order = questionary.select("Start with:", create_choices([
        ("asc", "the oldest streak" if sort_field == "date" else "the shortest streak"),
        ("desc", "the latest streak" if sort_field == "date" else "the longest streak")
    ])).ask()

    streaks = habit.get_all_streaks(sort_field, sort_order)
    if len(streaks) == 0:
        questionary.print("You haven't achieved any streaks yet 🥺")
    else:
        streaks_table = list(map(lambda streak: [streak["length"], streak["start"], streak["end"]], streaks))
        print(tabulate(streaks_table,
                       headers=[f"Length ({streaks[0]['unit']})", "From", "Until"],
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


def get_custom_date(qualifying_text: str, start_date: Optional[datetime] = None):
    dt = None
    while dt is None:
        date_text = questionary.text(f"Type the {qualifying_text} date in DD-MM-YYYY form (e.g. 23-05-2023):").ask()
        if len(date_text) == 0:
            questionary.print(f"You didn't type a {qualifying_text} date.")
            continue

        try:
            dt = datetime.strptime(date_text, "%d-%m-%Y")

            if qualifying_text == "ending" and dt < start_date:
                dt = None
                raise ValueError("this date comes before the starting date")
        except ValueError as e:
            questionary.print(f"Something doesn't quite look right: {e}.  " +
                              "Make sure you provide a valid date, in the specified format.")

    return dt


def show_completion_rate_menu(habit: Habit):
    date_ranges = create_choices([
        ("last_wk", "Last week"),
        ("last_mo", "Last month"),
        ("custom", "Custom"),
     ]) if habit.get_recurrence() == "daily" else create_choices([
        ("last_mo", "Last month"),
        ("last_6_mo", "Last 6 months"),
        ("custom", "Custom"),
    ])

    date_range_choice = questionary.select("Which date range would you like to see your completion rate for?",
                                           date_ranges).ask()

    today = datetime.today()

    if date_range_choice == "custom":
        start_date = get_custom_date("starting")
        end_date = get_custom_date("ending", start_date)
    else:
        start_date = None
        end_date = None

        if date_range_choice == "last_wk":
            start_date = today - timedelta(days=7)
        elif date_range_choice == "last_mo":
            if today.month == 1:
                start_date = datetime(today.year - 1, 12, today.day)
            else:
                try:
                    start_date = datetime(today.year, today.month - 1, today.day)
                except ValueError:
                    start_date = datetime(today.year, today.month, 1)
        elif date_range_choice == "last_6_mo":
            if today.month == 6:
                start_date = datetime(today.year - 1, 12, today.day)
            elif today.month < 6:
                try:
                    start_date = datetime(today.year - 1, (today.month - 6) % 12, today.day)
                except ValueError:
                    start_date = datetime(today.year - 1, (today.month - 6) % 12 + 1, 1)
            else:
                try:
                    start_date = datetime(today.year, today.month - 6, today.day)
                except ValueError:
                    start_date = datetime(today.year, (today.month - 6) + 1, 1)

    if start_date is not None:
        start_date = utils.strip_out_time(start_date)

        completion = habit.get_completion_rate(start_date, end_date)
        completion_message_intro = f"Since {start_date}, " if end_date is None \
            else f"From {start_date} to {end_date}, "
        completion_message = f"you have performed this habit on {completion['num_active_periods']} out of " +\
            f"{completion['num_total_periods']} {'days' if habit.get_recurrence() == 'daily' else 'weeks'}.\n" +\
            f"This is a completion rate of {round(100 * completion['rate'])}%."
        questionary.print(f"{completion_message_intro}{completion_message}")

    follow_up_action = questionary.select("What would you like to do next?", create_choices([
        ("different_date_range", "View your completion rate over a different date range"),
        ("habit_details", "Show the details of the habit"),
        ("exit", "Exit"),
    ])).ask()

    if follow_up_action == "different_date_range":
        show_completion_rate_menu(habit)
    elif follow_up_action == "habit_details":
        show_habit_actions_menu(habit)
    elif follow_up_action == "exit":
        sys.exit()


def show_delete_habit_menu(habit: Habit):
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
            show_habits_abridged()
        elif follow_up_action == "exit":
            sys.exit()
    else:
        show_habit_actions_menu(habit)


def show_select_columns_menu():
    columns = questionary.checkbox("Choose the details you would like to see:", create_choices([
        ("created_at", "Date the habit was created"),
        ("recurrence", "How often the habit should be performed"),
        ("last_performed", "When last the habit was performed"),
        ("num_periods_performed", "How many days/weeks the habit has been performed"),
        ("completion_rate", "How successfully you have completed the habit since creating it"),
        ("latest_streak", "The length of your latest streak"),
    ])).ask()

    return ["title"] + columns


def show_stats_menu():
    full_habits_list = analytics.get_habits()
    modified_list = []

    fields = {
        "title": {
            "label": "Title",
            "sort_options": {
                "asc": "A",
                "desc": "Z",
            },
        },
        "created_at": {
            "label": "Created at",
            "sort_options": {
                "asc": "the oldest habit",
                "desc": "the newest habit",
            },
        },
        "recurrence": {
            "label": "Recurs",
            "filters": {
                "options": [ "Remove the filter", "Show the daily habits", "Show the weekly habits" ],
                "current": 0,  # show unfiltered by default
            },
        },
        "last_performed": {
            "label": "Last performed",
            "sort_options": {
                "asc": "the habit performed least recently",
                "desc": "the habit performed most recently"
            },
        },
        "num_periods_performed": {
            "label": "# days/weeks performed",
            "sort_options": {
                "asc": "the habit performed on the fewest days/weeks",
                "desc": "the habit performed on the most days/weeks",
            },
        },
        "completion_rate": {
            "label": "Completion (%)",
            "sort_options": {
                "asc": "the habit completed least successfully",
                "desc": "the habit completed most successfully"
            },
        },
        "latest_streak": {
            "label": "Latest streak",
            "sort_options": {
                "asc": "the habit with the shortest streak",
                "desc": "the habit with the longest streak",
            },
        },
    }

    choice = "columns"
    columns = []
    filtered_headers = []

    while choice is not None:
        if choice == "columns":
            columns = show_select_columns_menu()
            filtered_headers = list(map(lambda key: fields[key]["label"], columns))

            modified_list = []
            for habit in full_habits_list:
                stats = {}
                for col in columns:
                    stats[col] = habit[col]
                modified_list.append(stats)
        elif choice == "sort":
            sort_columns = {
                key: props  # duplicate what's in the `fields` dictionary
                for (key, props) in fields.items()
                # only keep the columns that are visible and that are sortable on
                if key in columns and "sort_options" in fields[key]
            }
            sort_field = questionary.select("Which column would you like to sort on?", create_choices(
                [(key, sort_columns[key]["label"]) for key in sort_columns.keys()]
            )).ask()
            sort_order = questionary.select("Start from...", create_choices([
                ("asc", sort_columns[sort_field]["sort_options"]["asc"]),
                ("desc", sort_columns[sort_field]["sort_options"]["desc"]),
            ])).ask()
            modified_list = analytics.sort_habits(modified_list, sort_field, sort_order)
        elif choice == "filter":
            filter_columns = {
                key: props  # duplicate what's in the `fields` dictionary
                for (key, props) in fields.items()
                if "filters" in fields[key]  # only keep the fields that can be filtered on
            }
            filter_field = questionary.select("Which field would you like to filter on?", create_choices([
                (key, props["label"]) for (key, props) in filter_columns.items()
            ])).ask()
            filter_option = questionary.select("How would you like to update this filter?", create_choices([
                (idx, label)
                for (idx, label)
                in enumerate(filter_columns[filter_field]["filters"]["options"])
                if idx != filter_columns[filter_field]["filters"]["current"]
            ])).ask()
            # TODO: Extract these bits of logics into functions so that the processing can be reused
        elif choice == "home":
            show_home_menu()
            break
        elif choice == "exit":
            sys.exit()

        print(tabulate(map(
            lambda h: [value for (key, value) in h.items()],
            modified_list
        ), headers=filtered_headers))

        choice = questionary.select("What would you like to do next?", create_choices([
            ("columns", "Change the columns"),
            ("filter", "Change a filter"),
            ("sort", "Change the sort order"),
            ("home", "Go back home"),
            ("exit", "Exit"),
        ])).ask()



db.connect()
show_home_menu(True)
