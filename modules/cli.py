import sys
from datetime import datetime
from typing import Optional

import questionary
from tabulate import tabulate

from modules import habits, utils, analytics
from classes.habit import Habit


# TODO: Pause between actions to let user first digest outcome, and then choose next action
# TODO: Format dates nicely e.g. 23 December 2023
# TODO: Instead of just sys.exit, show a nice goodbye message then exit
# TODO: Headings to show where in the program the user is

def create_choices(options: list[tuple]):
    """
    Utility function to take a list of tuples and convert them to questionary Choice objects
    :param options: A list of tuples where each tuple has a key (the code for a user's action) and a label (the
    human-friendly text that will be displayed to the user to select this option), e.g. ("exit", "Exit the program")
    :return: A list of questionary Choice objects corresponding to the input list of options
    """
    return list(map(lambda opt: questionary.Choice(value=opt[0], title=opt[1]), options))


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
        show_create_habit_menu()
    elif action == "show_one":
        show_habits_abridged()
    elif action == "stats":
        show_stats_menu()
    elif action == "exit":
        sys.exit()


def show_create_habit_menu(follow_up: Optional[any] = None):
    """
    Present the UI to create a new habit
    :param follow_up: A function to call after successfully creating the habit
    """
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
    """
    Post creating a new habit, this menu allows the user to mark it as done for the day/week/etc.
    :param habit: The newly-created habit
    """
    action = questionary.select("What would you like to do next?", create_choices([
        ("perform", f"Mark this habit as done for the {habit.get_interval()}"),
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
    """
    The sequence for performing a habit
    :param habit: The habit to be marked as having been performed
    :param next_menu: A function to be invoked once the habit has been performed, to show the next menu
    """
    habit.perform()
    questionary.print(
        f"You've marked the habit '{habit.get_title()}' as done for the {habit.get_interval()}; nice!",
        style="fg:lime")
    if next_menu is not None:
        next_menu()
    else:
        show_home_menu()


def show_habits_abridged():
    """
    Show a list of the habits' titles for the user to select from, in order for them to execute some action on that
    habit
    """
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


def get_latest_streak_message(streak: dict, recurrence: str):
    """
    Utility function to create a message based on the kind of streak the user has achieved most recently
    :param streak: The object describing the user's latest streak
    :param recurrence: How often the habit is meant to be performed
    :return: A message to encourage the user to either start a new streak or maintain their current one
    """
    if streak["start"] is None:
        return "You haven't had any streaks yet, so today feels like a good day to kick one off 🚀"

    interval = "day" if recurrence == "daily" else "week"

    if streak["is_current"] is False:  # most recent streak was broken
        part_1 = f"Your last streak ran from {streak['start']} until {streak['end']}"
        part_2 = f"— a {'decent' if streak['length'] <= 4 else 'whopping'}"
        part_3 = f"{streak['length']} {interval}{'' if streak['length'] == 1 else 's'}!"
        part_4 = "Today feels like a good day to start a new one 🚀"

        return f"{part_1} {part_2} {part_3}  {part_4}"

    part_1 = "You are currently on a roll!"
    part_2 = f"You've kept up this habit for {streak['length']} {interval}{'' if streak['length'] == 1 else 's'} 🥳"

    if streak["can_extend_today"] is False:  # streak is ongoing; must continue next interval
        part_3 = f"Remember to perform this habit again {'tomorrow' if recurrence == 'daily' else 'next week'}."
    else:  # streak needs to be continued today/this week, otherwise it will be broken
        part_3 = f"To maintain your streak, be sure to perform this habit again before the end of {
            'today' if recurrence == 'daily' else 'this week'}."

    return f"{part_1}  {part_2}  {part_3}"


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
        ("perform", f"Mark this habit as done for the {habit.get_interval()}"),
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
        streaks_table = list(map(lambda streak: [streak["length"], streak["start"], streak["end"]], streaks))
        print(tabulate(streaks_table,
                       headers=[f"Length ({habit.get_interval()}s)", "From", "Until"],
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


def get_custom_date_range():
    """
    Displays UI to get a date range from the user
    :return: A tuple containing datetime objects for the start and end date desired by the user
    """
    start = end = None

    for date_type in ["starting", "ending"]:
        dt = None
        while dt is None:
            date_text = questionary.text(f"Type the {date_type} date in DD-MM-YYYY form (e.g. 23-05-2023):").ask()
            # Don't accept a blank
            # (although in future it would be nice to support open-ended date ranges :))
            if len(date_text) == 0:
                questionary.print(f"You didn't type {'a starting' if date_type == 'starting' else 'an ending'} date.")
                continue

            try:
                # Attempt to create a datetime object from the date string supplied.  If the creation fails, we know
                # either the user didn't follow the correct format or the date they've chosen doesn't exist...
                dt = datetime.strptime(f"{date_text} {'00:00:00' if date_type == 'starting' else '23:59:59'}",
                                       "%d-%m-%Y %H:%M:%S")

                # If the user is specifying an end date for the range, we need to check that the end date comes after
                # the start date they chose
                if date_type == "ending" and dt < start:
                    dt = None
                    raise ValueError("this date comes before the starting date")

                # If the date survived all the checks, then we can put it into its official store
                if date_type == "starting":
                    start = dt
                else:
                    end = dt
            except ValueError as e:
                questionary.print(f"Something doesn't quite look right: {e}.  " +
                                  "Make sure you provide a valid date, in the specified format.")

    return start, end


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
            (start_date, end_date) = utils.get_last_week_date_range()
        elif date_range_choice == "last_mo":
            (start_date, end_date) = utils.get_last_month_date_range()
        else:
            (start_date, end_date) = utils.get_last_6_months_date_range()

    # Cap the date range so that it does not go beyond the date when the habit was created
    start_date = max(start_date, habit.get_created_at())
    completion = habit.get_completion_rate(start_date, end_date)

    completion_message_intro = f"From {start_date} to {end_date},"
    completion_message = f"you have performed this habit on {completion['num_active_periods']} out of " +\
        f"{completion['num_total_periods']} {habit.get_interval(completion['num_total_periods'])}.\n" +\
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
            show_habits_abridged()
        elif follow_up_action == "exit":
            sys.exit()
    else:
        show_habit_actions_menu(habit)


def show_select_columns_menu():
    """
    Let the user decide which properties they want to view in the full list of their habits
    :return: The list of properties the user would like to view, where "title" is always included
    """
    columns = questionary.checkbox("Choose the details you would like to see:", create_choices([
        ("created_at", "Date the habit was created"),
        ("recurrence", "How often the habit should be performed"),
        ("last_performed", "When last the habit was performed"),
        ("num_periods_performed", "How many days/weeks the habit has been performed"),
        ("completion_rate", "How successfully you have completed the habit since creating it"),
        ("latest_streak", "The length of your latest streak"),
    ])).ask()

    return ["title"] + columns


stats_fields = {
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
                "options": [
                    ("none", "Remove the filter"),
                    ("daily", "Show the daily habits"),
                    ("weekly", "Show the weekly habits")
                ],
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


def get_requested_habit_properties(habits_list: list, requested_props: list):
    """
    Given a list of the user's habits (from the analytics module) and a list of the properties the user wants to see
    (e.g. date the habit was last performed, length of the latest streak for each habit), return the list of the user's
    habits with just those properties, not the full set of the stats properties.
    :param habits_list: A subset of or all the user's habits, as returned by the analytics module
    :param requested_props: The list of properties that the user wants to see for each habit
    :return: A list of habits with only the `requested_props` properties
    """
    return [{
        key: value for (key, value) in habit.items()
        if key in requested_props  # for each habit item, only copy the stats prop if it is one of the requested ones
    } for habit in habits_list]


def get_sortable_columns(visible_columns: list):
    """
    Which of the columns in `stats_fields` can be used to sort the user's habits?
    :param visible_columns: The list of properties (stats) that the user is currently viewing
    :return: The subset of `visible_columns` that can be used to sort the user's habits
    """
    return {
        key: props  # duplicate what's in the `stats_fields` dictionary
        for (key, props) in stats_fields.items()
        # only keep the columns that are visible and that are sortable on
        if key in visible_columns and "sort_options" in stats_fields[key]
    }


def get_filterable_columns():
    return {
        key: props  # duplicate what's in the `stats_fields` dictionary
        for (key, props) in stats_fields.items()
        if "filters" in stats_fields[key]  # only keep the fields that can be filtered on
    }


def show_stats_menu():
    full_habits_list = analytics.get_habits()  # to be kept pristine
    modified_habits_list = None  # this will be the list that gets displayed and therefore shows changes like sorting

    action = "columns"  # the first action will always be for the user to select the columns they want to see
    columns = []  # the columns the user wants to see
    filtered_headers = []  # the human-friendly labels for the columns the user wants to see

    # We need to remember to sorting configuration as filters are applied/removed
    sort_field = None
    sort_order = None

    # Also need to remember the filter settings for when we update visible columns
    filter_field = None
    filter_option = "none"

    # Reset filters
    for field in stats_fields.keys():
        if "filters" in stats_fields[field]:
            stats_fields[field]["filters"]["current"] = "none"

    # TODO - FIX BUG: Choose a sort column.  Then choose different set of columns to view, excluding sort column.
    # sort function is not happy because sort prop is no longer present in the array passed to it.  Larger question:
    # Should user be able to sort on column that isn't visible??  Good UX for selecting different columns... reset sort?
    while action is not None:
        if action == "columns":
            columns = show_select_columns_menu()
            filtered_headers = list(map(lambda column: stats_fields[column]["label"], columns))
            # Show only desired columns
            modified_habits_list = get_requested_habit_properties(full_habits_list, columns)

            # Restore filtering
            if filter_field is not None:
                modified_habits_list = analytics.filter_habits(modified_habits_list, filter_field, filter_option)
            # Restore sorting
            if sort_field is not None:
                modified_habits_list = analytics.sort_habits(modified_habits_list, sort_field, sort_order)

        elif action == "sort":
            sort_columns = get_sortable_columns(columns)
            sort_field = questionary.select("Which column would you like to sort on?", create_choices(
                # create tuples like ("completion_rate", "Completion (%)")
                [(key, sort_columns[key]["label"]) for key in sort_columns.keys()]
            )).ask()
            sort_order = questionary.select("Start from:", create_choices([
                ("asc", sort_columns[sort_field]["sort_options"]["asc"]),
                ("desc", sort_columns[sort_field]["sort_options"]["desc"]),
            ])).ask()
            modified_habits_list = analytics.sort_habits(modified_habits_list, sort_field, sort_order)

        elif action == "filter":
            filter_columns = get_filterable_columns()
            filter_field = questionary.select("Which field would you like to filter on?", create_choices([
                (key, props["label"]) for (key, props) in filter_columns.items()
            ])).ask()
            filter_option = questionary.select("How would you like to update this filter?", create_choices([
                (key, label)
                for (key, label)
                in filter_columns[filter_field]["filters"]["options"]
                if key != filter_option  # Omit the option that is currently selected
            ])).ask()

            if filter_option == "none":
                # Restore to original list
                modified_habits_list = get_requested_habit_properties(full_habits_list, columns)
            else:
                # Filter full list of habits
                filtered_habits = analytics.filter_habits(full_habits_list, filter_field, filter_option)
                # Show only desired columns
                modified_habits_list = get_requested_habit_properties(filtered_habits, columns)

            # If sort was applied before, re-apply to updated list
            if sort_field is not None:
                modified_habits_list = analytics.sort_habits(modified_habits_list, sort_field, sort_order)

        elif action == "home":
            show_home_menu()
            break
        elif action == "exit":
            sys.exit()

        print(tabulate(map(
            lambda h: [value for (key, value) in h.items()],
            modified_habits_list
        ), headers=filtered_headers))

        action = questionary.select("What would you like to do next?", create_choices([
            ("columns", "Change the columns"),
            ("filter", "Change a filter"),
            ("sort", "Change the sort order"),
            ("home", "Go back home"),
            ("exit", "Exit"),
        ])).ask()
