from datetime import datetime, timedelta
from modules import db, utils
from classes.habit import Habit

class TestCompletionRate:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_with_start_and_end_date(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")
            day_habit.perform("2023-06-13 20:54:09")
            day_habit.perform("2023-07-03 22:21:16")

            completion_stats = day_habit.get_completion_rate(
                utils.to_datetime("2023-06-03 10:45:12"),
                utils.to_datetime("2023-06-28 01:32:51")
            )

            assert completion_stats["num_active_periods"] == 2
            assert completion_stats["num_total_periods"] == 26
            perc = round(100 * completion_stats["rate"])
            assert perc == 8

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            completion_stats = week_habit.get_completion_rate(
                utils.to_datetime("2023-06-03 10:45:12"),
                utils.to_datetime("2023-06-28 01:32:51")
            )

            assert completion_stats["num_active_periods"] == 3
            assert completion_stats["num_total_periods"] == 5
            perc = round(100 * completion_stats["rate"])
            assert perc == 60

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_with_start_date_only(self):
        def test_for_daily_habit():
            today = datetime.today()
            creation_date = today - timedelta(days=37)
            day_habit = Habit("Practise piano", "daily", creation_date.strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=16)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=36)).strftime("%Y-%m-%d %H:%M:%S"))

            completion_stats = day_habit.get_completion_rate(creation_date + timedelta(days=6))

            assert completion_stats["num_active_periods"] == 3
            assert completion_stats["num_total_periods"] == 32
            perc = round(100 * completion_stats["rate"])
            assert perc == 9

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            today = datetime.today()
            creation_date = today - (timedelta(days=(today.weekday() + 29)))  # a Sunday
            week_habit = Habit("Phone parents", "weekly", creation_date.strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=20)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"))

            completion_stats = week_habit.get_completion_rate(creation_date + timedelta(days=6))

            assert completion_stats["num_active_periods"] == 3
            assert completion_stats["num_total_periods"] == 5
            perc = round(100 * completion_stats["rate"])
            assert perc == 60

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_with_end_date_only(self):
        def test_for_daily_habit():
            day_habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
            day_habit.perform("2023-05-29 00:12:32")
            day_habit.perform("2023-05-31 14:54:22")
            day_habit.perform("2023-06-11 06:55:12")
            day_habit.perform("2023-06-13 20:54:09")
            day_habit.perform("2023-07-03 22:21:16")

            completion_stats = day_habit.get_completion_rate(
                end_date=utils.to_datetime("2023-06-28 01:32:51")
            )

            assert completion_stats["num_active_periods"] == 4
            assert completion_stats["num_total_periods"] == 32
            perc = round(100 * completion_stats["rate"])
            assert perc == 12  # Note that rounding (x + 1/2) goes to nearest EVEN number

        def test_for_weekly_habit():
            week_habit = Habit("Phone parents", "weekly", "2023-05-28 19:04:55")
            week_habit.perform("2023-05-29 00:12:32")
            week_habit.perform("2023-05-31 14:54:22")
            week_habit.perform("2023-06-11 06:55:10")
            week_habit.perform("2023-06-17 18:25:43")
            week_habit.perform("2023-06-25 20:46:06")

            completion_stats = week_habit.get_completion_rate(
                end_date=utils.to_datetime("2023-06-28 01:32:51")
            )

            assert completion_stats["num_active_periods"] == 4
            assert completion_stats["num_total_periods"] == 6
            perc = round(100 * completion_stats["rate"])
            assert perc == 67

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_with_no_date_restriction(self):
        def test_for_daily_habit():
            today = datetime.today()
            creation_date = today - timedelta(days=37)
            day_habit = Habit("Practise piano", "daily", creation_date.strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=16)).strftime("%Y-%m-%d %H:%M:%S"))
            day_habit.perform((creation_date + timedelta(days=36)).strftime("%Y-%m-%d %H:%M:%S"))

            completion_stats = day_habit.get_completion_rate()

            assert completion_stats["num_active_periods"] == 5
            assert completion_stats["num_total_periods"] == 38
            perc = round(100 * completion_stats["rate"])
            assert perc == 13

        def test_for_weekly_habit():
            today = datetime.today()
            creation_date = today - (timedelta(days=(today.weekday() + 29)))  # a Sunday
            week_habit = Habit("Phone parents", "weekly", creation_date.strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=0)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=13)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=19)).strftime("%Y-%m-%d %H:%M:%S"))
            week_habit.perform((creation_date + timedelta(days=27)).strftime("%Y-%m-%d %H:%M:%S"))

            completion_stats = week_habit.get_completion_rate()

            assert completion_stats["num_active_periods"] == 5
            assert completion_stats["num_total_periods"] == 6
            perc = round(100 * completion_stats["rate"])
            assert perc == 83

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_with_no_activities(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:04:55")
        completion_stats = habit.get_completion_rate(end_date=datetime(2023, 5, 29, 14, 23, 12))
        assert completion_stats["num_active_periods"] == 0
        assert completion_stats["num_total_periods"] == 2
        assert completion_stats["rate"] == 0

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()