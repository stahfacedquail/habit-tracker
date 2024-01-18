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


def show_habit_actions_menu(habit: Habit):
    # TODO Format dates nicely e.g. 23 December 2023
    latest_streak = habit.get_latest_streak()

    last_performed = habit.get_date_last_performed()
    questionary.print(f"""
Title: {habit.get_title()}
Date created: {habit.get_created_at()}
Recurrence: {habit.get_recurrence()}
Last performed: {last_performed if last_performed is not None else "No activities recorded yet"}
    """)


db.connect()
show_home_menu(True)
