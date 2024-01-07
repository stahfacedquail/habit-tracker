import db
import utils
from datetime import datetime
from classes.habit import Habit


class TestUtils:
    def test_to_datetime(self):
        dt_string = "2023-08-11 19:01:23"
        dt = utils.to_datetime(dt_string)
        assert dt.day == 11
        assert dt.month == 8
        assert dt.year == 2023
        assert dt.hour == 19
        assert dt.minute == 1
        assert dt.second == 23

    def test_to_date_only_string(self):
        dt = datetime(2023, 12, 25, 15, 22, 0)
        dt_string = utils.to_date_only_string(dt)
        assert dt_string == "2023-12-25"

    def test_strip_out_time(self):
        dt = datetime(2023, 12, 25, 15, 22, 45)
        zeroed_dt = utils.strip_out_time(dt)
        assert zeroed_dt.day == 25
        assert zeroed_dt.month == 12
        assert zeroed_dt.year == 2023
        assert zeroed_dt.hour == 0
        assert zeroed_dt.minute == 0
        assert zeroed_dt.second == 0

    def test_get_num_days_from_to(self):
        start_dt = datetime(2023, 12, 29, 18, 0, 55)
        end_dt = datetime(2023, 12, 31, 1, 57, 19)

        def test_inclusive_of_end_date():
            diff = utils.get_num_days_from_to(start_dt, end_dt)
            assert diff == 3

        def test_exclusive_of_end_date():
            diff = utils.get_num_days_from_to(start_dt, end_dt, False)
            assert diff == 2

        test_inclusive_of_end_date()
        test_exclusive_of_end_date()

    def test_get_num_weeks_from_to(self):
        def test_same_week():
            date_a = datetime(2023, 12, 1, 18, 0, 55)
            date_b = datetime(2023, 12, 3, 1, 57, 19)

            diff = utils.get_num_weeks_from_to(date_a, date_b)
            assert diff == 1

        def test_diff_weeks():
            date_a = datetime(2023, 12, 1, 18, 0, 55)
            date_b = datetime(2023, 12, 26, 1, 57, 19)

            diff = utils.get_num_weeks_from_to(date_a, date_b)
            assert diff == 5

        def test_diff_weeks_by_1_day():
            date_a = datetime(2023, 12, 3, 18, 0, 55)
            date_b = datetime(2023, 12, 4, 1, 57, 19)

            diff = utils.get_num_weeks_from_to(date_a, date_b)
            assert diff == 2

        test_same_week()
        test_diff_weeks()
        test_diff_weeks_by_1_day()

    def test_get_week_start_date(self):
        def test_non_monday_dt():
            dt = datetime(2023, 12, 1, 5, 12, 19)
            week_start_dt = utils.get_week_start_date(dt)
            assert week_start_dt.year == 2023
            assert week_start_dt.month == 11
            assert week_start_dt.day == 27
            assert week_start_dt.hour == 0
            assert week_start_dt.minute == 0
            assert week_start_dt.second == 0

        def test_monday_dt():
            dt = datetime(2023, 7, 24, 5, 12, 19)
            week_start_dt = utils.get_week_start_date(dt)
            assert week_start_dt.year == 2023
            assert week_start_dt.month == 7
            assert week_start_dt.day == 24
            assert week_start_dt.hour == 0
            assert week_start_dt.minute == 0
            assert week_start_dt.second == 0

        test_non_monday_dt()
        test_monday_dt()

    def test_grouping(self):
        def setup_method():
            db.connect("test.db")
            db.setup_tables()

        def teardown_method():
            db.remove_tables()
            db.disconnect()

        def test_no_activities():
            habit = Habit("Practise piano", "daily", "2023-05-28 18:15:32")
            grouped_by_dt = utils.group_activities_by_performance_period(habit.get_activities(), habit.get_recurrence())
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 0

        def test_grouping_by_day():
            habit = Habit("Practise piano", "daily", "2023-05-28 18:15:32")
            habit.perform("2023-05-29 20:12:12")
            habit.perform("2023-05-29 22:05:56")
            habit.perform("2023-06-03 01:37:05")
            grouped_by_dt = utils.group_activities_by_performance_period(habit.get_activities(), habit.get_recurrence())
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 2
            assert len(grouped_by_dt["2023-05-29"]) == 2
            assert len(grouped_by_dt["2023-06-03"]) == 1

        def test_grouping_by_week():
            habit = Habit("Phone parents", "weekly", "2023-05-28 18:15:32")
            habit.perform("2023-05-31 20:12:12")
            habit.perform("2023-06-02 22:05:56")
            habit.perform("2023-06-02 01:37:05")
            habit.perform("2023-06-24 21:04:22")
            grouped_by_dt = utils.group_activities_by_performance_period(habit.get_activities(), habit.get_recurrence())
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 2
            assert len(grouped_by_dt["2023-05-29"]) == 3
            assert len(grouped_by_dt["2023-06-19"]) == 1

        # TODO: Test filtering

        setup_method()
        test_no_activities()
        test_grouping_by_day()
        test_grouping_by_week()
        teardown_method()

    def test_get_accurate_streak_params(self):
        def setup_method():
            db.connect("test.db")
            db.setup_tables()

        def teardown_method():
            db.remove_tables()
            db.disconnect()

        setup_method()

        habit = Habit("Phone parents", "weekly", "2023-09-14 20:01:16")
        habit.perform("2023-09-18 16:20:30")
        habit.perform("2023-09-21 16:42:11")
        habit.perform("2023-09-21 21:30:31")
        habit.perform("2023-09-23 20:30:47")
        habit.perform("2023-09-27 05:16:00")
        habit.perform("2023-09-27 13:00:01")
        habit.perform("2023-09-27 20:57:17")
        week_1_activities = list(filter(
            lambda activity: utils.to_datetime("2023-09-18 00:00:00")
            <= activity.get_performed_at()
            < utils.to_datetime("2023-09-25 00:00:00"), habit.get_activities()))
        week_2_activities = list(filter(
            lambda activity: utils.to_datetime("2023-09-25 00:00:00")
            <= activity.get_performed_at()
            < utils.to_datetime("2023-10-02 00:00:00"), habit.get_activities()))
        params = utils.get_streak_accurate_params(
            week_1_activities,
            week_2_activities,
            habit
        )

        assert params["start"] == utils.to_datetime("2023-09-18 16:20:30")
        assert params["end"] == utils.to_datetime("2023-09-27 20:57:17")
        assert params["length"] == 2
        assert params["unit"] == "weeks"

        teardown_method()

