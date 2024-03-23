import sys

from typing import Optional
import questionary
from datetime import datetime

from classes.habit import Habit
from modules import db
from modules.utils import prettify_datetime, get_start_of_day, get_end_of_day


def create_choices(options: list[tuple], pre_selections: Optional[list[str]] = None):
    """
    Utility function to take a list of tuples and convert them to questionary Choice objects
    :param options: A list of tuples where each tuple has a key (the code for a user's action) and a label (the
    human-friendly text that will be displayed to the user to select this option), e.g. ("exit", "Exit the program")
    :param pre_selections: A list of the values that should be pre-selected
    :return: A list of questionary Choice objects corresponding to the input list of options
    """
    if pre_selections is None:
        choices = list(map(lambda opt: questionary.Choice(value=opt[0], title=opt[1]), options))
    else:
        choices = list(map(lambda opt: questionary.Choice(
            value=opt[0], title=opt[1], checked=(opt[0] in pre_selections)
        ), options))

    return choices


def perform_habit(habit: Habit, show_next_menu):
    """
    The sequence for performing a habit
    :param habit: The habit to be marked as having been performed
    :param show_next_menu: A function to be invoked once the habit has been performed, to show the next menu
    """
    habit.perform()
    questionary.print(
        f"You've marked the habit '{habit.get_title()}' as done for the {habit.get_interval_label()}; nice!",
        style="fg:lime")

    questionary.press_any_key_to_continue().ask()
    show_next_menu()


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
        if streak["length"] > 1:
            part_1 = f"Your last streak ran from {prettify_datetime(streak['start'])} until {prettify_datetime(streak['end'])}"
            part_2 = f"— a {'decent' if streak['length'] <= 4 else 'whopping'}"
            part_3 = f"{streak['length']} {interval}{'' if streak['length'] == 1 else 's'}!"
            part_4 = "Today feels like a good day to start a new one 🚀"
            return f"{part_1} {part_2} {part_3}  {part_4}"

        part_1 = f"The last time you performed this habit was on {prettify_datetime(streak['start'])};"
        part_2 = f"you managed to keep it up for a {interval}!"
        part_3 = "Today feels like a good day to pick up again 🚀"
        return f"{part_1} {part_2} {part_3}"

    part_1 = "You are currently on a roll!"
    part_2 = f"You've kept up this habit for {streak['length']} {interval}{'' if streak['length'] == 1 else 's'} 🥳"

    if streak["can_extend_today"] is False:  # streak is ongoing; must continue next interval
        part_3 = f"Remember to perform this habit again {'tomorrow' if recurrence == 'daily' else 'next week'}."
    else:  # streak needs to be continued today/this week, otherwise it will be broken
        part_3 = f"To maintain your streak, be sure to perform this habit again before the end of {
            'today' if recurrence == 'daily' else 'this week'}."

    return f"{part_1}  {part_2}  {part_3}"


def get_custom_date_range():
    """
    Displays UI to get a date range from the user (local time)
    :return: A tuple containing datetime objects for the start and end date desired by the user (local time)
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
                dt = datetime.strptime(f"{date_text}", "%d-%m-%Y")
                dt = get_start_of_day(dt) if date_text == 'starting' else get_end_of_day(dt)

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


def close_app():
    """
    Before exiting the program, close the database connection and print a goodbye message.
    """
    db.disconnect()
    questionary.print("Cheerio! :)")
    sys.exit(0)
