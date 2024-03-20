from modules import db
from modules.utils import to_datetime
from classes.habit import Habit


class TestCompletionCount:
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

    def test_multiple_periods_completed(self):
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

    def test_filtered_by_start_and_end_date(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")
            day_habit.perform("2023-06-13 20:54:09")
            day_habit.perform("2023-07-03 22:21:16")

            num_times_completed = day_habit.get_number_of_times_completed(
                to_datetime("2023-06-03 10:45:12"),
                to_datetime("2023-06-28 01:32:51")
            )
            assert num_times_completed == 2

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            num_times_completed = week_habit.get_number_of_times_completed(
                to_datetime("2023-06-03 10:45:12"),
                to_datetime("2023-06-28 01:32:51")
            )
            assert num_times_completed == 3

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_filtered_by_start_date(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")
            day_habit.perform("2023-06-13 20:54:09")
            day_habit.perform("2023-07-03 22:21:16")

            num_times_completed = day_habit.get_number_of_times_completed(
                to_datetime("2023-06-03 10:45:12")
            )
            assert num_times_completed == 3

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            num_times_completed = week_habit.get_number_of_times_completed(
                to_datetime("2023-06-17 00:00:01")
            )
            assert num_times_completed == 2

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_filtered_by_end_date(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")
            day_habit.perform("2023-06-13 20:54:09")
            day_habit.perform("2023-07-03 22:21:16")

            num_times_completed = day_habit.get_number_of_times_completed(
                end_date=to_datetime("2023-06-11 18:32:51")
            )
            assert num_times_completed == 3

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            num_times_completed = week_habit.get_number_of_times_completed(
                end_date=to_datetime("2023-05-31 01:32:51")
            )
            assert num_times_completed == 1

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_filter_returns_no_activities(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")
            day_habit.perform("2023-06-13 20:54:09")
            day_habit.perform("2023-07-03 22:21:16")

            num_times_completed = day_habit.get_number_of_times_completed(
                end_date=to_datetime("2023-05-28 23:45:12")
            )
            assert num_times_completed == 0

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            num_times_completed = week_habit.get_number_of_times_completed(
                to_datetime("2023-06-28 10:45:12"),
                to_datetime("2023-06-30 01:32:51")
            )
            assert num_times_completed == 0

        test_for_daily_habit()
        test_for_weekly_habit()

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
