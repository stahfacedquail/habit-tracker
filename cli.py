import questionary
from typing import Optional
import sys
import db
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
        pass
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
        pass
    elif action == "completion":
        pass
    elif action == "delete":
        pass
    elif action == "back":
        show_habits_abridged()
    elif action == "exit":
        sys.exit()


db.connect()
show_home_menu(True)
