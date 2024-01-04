import pytest
from datetime import date
import db
import utils
from classes.habit import Habit


class TestHabit:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_create_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        assert habit.get_uuid() is not None
        assert habit.get_title() == "Practise piano"
        assert habit.get_recurrence() == "daily"
        assert habit.get_created_at() == utils.to_datetime("2023-05-28 18:57:19")
        assert len(habit.get_activities()) == 0

    def test_create_habit_with_db_timestamp(self):
        habit = Habit("Water plants", "weekly")
        assert habit.get_uuid() is not None
        assert habit.get_title() == "Water plants"
        assert habit.get_recurrence() == "weekly"
        assert habit.get_created_at() is not None
        assert habit.get_created_at().day == date.today().day
        assert habit.get_created_at().month == date.today().month
        assert habit.get_created_at().year == date.today().year
        assert len(habit.get_activities()) == 0

    def test_perform_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        habit.perform("2023-05-29 21:00:43")
        assert len(habit.get_activities()) == 1
        execution = habit.get_activities()[0]
        assert execution.get_uuid() is not None
        assert execution.get_habit_uuid() == habit.get_uuid()
        assert execution.get_performed_at() == utils.to_datetime("2023-05-29 21:00:43")

    def test_perform_habit_with_db_timestamp(self):
        habit = Habit("Practise piano", "daily")
        habit.perform()
        assert len(habit.get_activities()) == 1
        execution = habit.get_activities()[0]
        assert execution.get_uuid() is not None
        assert execution.get_habit_uuid() == habit.get_uuid()
        assert execution.get_performed_at().day == date.today().day
        assert execution.get_performed_at().month == date.today().month
        assert execution.get_performed_at().year == date.today().year

    def test_to_string(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        habit_string = str(habit).split("\n")
        assert habit_string[0] == "Title: Practise piano"
        assert habit_string[1] == "Recurs: daily"
        assert habit_string[2] == "Created at: 2023-05-28 18:57:19"
        assert habit_string[3] == "Has been performed 0 times"

        habit.perform()
        habit_string = str(habit).split("\n")
        assert habit_string[3] == "Has been performed 1 time"

        habit.perform()
        habit.perform()
        habit.perform()
        habit_string = str(habit).split("\n")
        assert habit_string[3] == "Has been performed 4 times"

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
