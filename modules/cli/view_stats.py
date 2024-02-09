import sys

import questionary
from typing import Optional, Callable
from tabulate import tabulate

from modules.cli.utils import create_choices
from modules import analytics

# Stores the function to invoke in order to show the Home menu (avoiding exporting it from original module and causing
# circular imports)
show_home_menu = lambda: None  # noop as initial value

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


def show_select_columns_menu(pre_selected_columns: Optional[list[str]] = None):
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
    ], pre_selected_columns)).ask()

    return ["title"] + columns


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


def show_stats_menu(show_home_menu_fn: Callable):
    """
    Display the user's statistics for all their habits
    :param show_home_menu_fn: The function to invoke in order to show the Home menu
    """
    global show_home_menu
    show_home_menu = show_home_menu_fn

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
            columns = show_select_columns_menu(columns if len(columns) > 0 else None)
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

            modified_habits_list = get_requested_habit_properties(  # Extract only the columns the user wants to see
                analytics.sort_habits(full_habits_list, sort_field, sort_order), columns
            )

            # If there was a filter, restore it
            if filter_field is not None:
                modified_habits_list = analytics.filter_habits(modified_habits_list, filter_field, filter_option)

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
                filter_field = None
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
