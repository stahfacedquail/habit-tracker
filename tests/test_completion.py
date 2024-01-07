import db
import utils
from classes.habit import Habit


class TestCompletionRate:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_no_activities(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            num_times_completed = day_habit.get_number_of_times_completed()
            assert num_times_completed == 0

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            num_times_completed = week_habit.get_number_of_times_completed()
            assert num_times_completed == 0

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_one_period_completed(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-06-01 15:15:38")
            num_times_completed = day_habit.get_number_of_times_completed()
            assert num_times_completed == 1

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            num_times_completed = week_habit.get_number_of_times_completed()
            assert num_times_completed == 1

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_multiple_performances_one_completion(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-29 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")

            num_times_completed = day_habit.get_number_of_times_completed()
            assert num_times_completed == 2

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:12")
            week_habit.perform("2023-06-11 18:05:03")

            num_times_completed = week_habit.get_number_of_times_completed()
            assert num_times_completed == 2

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_multiple_per_period(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")

            num_times_completed = day_habit.get_number_of_times_completed()
            assert num_times_completed == 3

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:12")

            num_times_completed = week_habit.get_number_of_times_completed()
            assert num_times_completed == 2

        test_for_daily_habit()
        test_for_weekly_habit()

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()