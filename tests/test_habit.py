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
        assert habit.uuid is not None
        assert habit.title == "Practise piano"
        assert habit.recurrence == "daily"
        assert habit.created_at == utils.to_datetime("2023-05-28 18:57:19")
        assert len(habit.activities) == 0

    def test_create_habit_with_db_timestamp(self):
        habit = Habit("Water plants", "weekly")
        assert habit.uuid is not None
        assert habit.title == "Water plants"
        assert habit.recurrence == "weekly"
        assert habit.created_at is not None
        assert habit.created_at.day == date.today().day
        assert habit.created_at.month == date.today().month
        assert habit.created_at.year == date.today().year
        assert len(habit.activities) == 0

    def test_perform_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        habit.perform("2023-05-29 21:00:43")
        assert len(habit.activities) == 1
        execution = habit.activities[0]
        assert execution.uuid is not None
        assert execution.habit == habit.uuid
        assert execution.performed_at == utils.to_datetime("2023-05-29 21:00:43")

    def test_perform_habit_with_db_timestamp(self):
        habit = Habit("Practise piano", "daily")
        habit.perform()
        assert len(habit.activities) == 1
        execution = habit.activities[0]
        assert execution.uuid is not None
        assert execution.habit == habit.uuid
        assert execution.performed_at.day == date.today().day
        assert execution.performed_at.month == date.today().month
        assert execution.performed_at.year == date.today().year

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
