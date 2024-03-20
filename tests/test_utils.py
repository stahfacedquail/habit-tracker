from freezegun import freeze_time
from datetime import datetime, timezone
from modules import db, utils
from classes.habit import Habit


class TestUtils:
    @freeze_time(tz_offset=+5)
    def test_get_as_local_time(self):
        t = datetime(year=2024, month=4, day=28, hour=6, minute=11, second=55, tzinfo=timezone.utc)
        local_t = utils.get_as_local_time(t).strftime("%Y-%m-%d %H:%M:%S")
        assert local_t == "2024-04-28 11:11:55"

    @freeze_time(tz_offset=-3)
    def test_get_as_gmt(self):
        local_t = datetime(year=2024, month=4, day=28, hour=6, minute=11, second=55)
        gmt_t = utils.get_as_gmt(local_t).strftime("%Y-%m-%d %H:%M:%S")
        assert gmt_t == "2024-04-28 09:11:55"

    @freeze_time(tz_offset=+8)
    def test_format_time_for_db(self):
        local_t = "2024-12-03 18:52:06"
        gmt_t = utils.format_date_for_db(local_t)
        assert gmt_t == "2024-12-03 10:52:06"

    def test_to_datetime_with_local_time_input(self):
        dt_string = "2023-08-11 19:01:23"
        dt = utils.to_datetime(dt_string)
        assert dt.day == 11
        assert dt.month == 8
        assert dt.year == 2023
        assert dt.hour == 19
        assert dt.minute == 1
        assert dt.second == 23

    @freeze_time(tz_offset=-2)
    def test_to_datetime_with_gmt_time_input(self):
        dt_string = "2023-08-11 19:01:23"
        dt = utils.to_datetime(dt_string, True)
        assert dt.day == 11
        assert dt.month == 8
        assert dt.year == 2023
        assert dt.hour == 17
        assert dt.minute == 1
        assert dt.second == 23

    def test_to_date_only_string(self):
        dt = datetime(2023, 12, 25, 15, 22, 0)
        dt_string = utils.to_date_only_string(dt)
        assert dt_string == "2023-12-25"

    def test_get_start_of_day(self):
        dt = datetime(2023, 12, 25, 15, 22, 45)
        zeroed_dt = utils.get_start_of_day(dt)
        assert zeroed_dt.day == 25
        assert zeroed_dt.month == 12
        assert zeroed_dt.year == 2023
        assert zeroed_dt.hour == 0
        assert zeroed_dt.minute == 0
        assert zeroed_dt.second == 0

    def test_prettify_date(self):
        dt = datetime(2023, 12, 5, 8, 5, 34)
        assert utils.prettify_datetime(dt) == "5 December 2023, 08:05"
        assert utils.prettify_datetime(dt, False) == "5 December 2023"

    def test_get_num_days_from_to(self):
        def test_inclusive_of_end_date():
            start_dt = datetime(2023, 12, 29, 18, 0, 55)
            end_dt = datetime(2023, 12, 31, 1, 57, 19)
            diff = utils.get_num_days_from_to(start_dt, end_dt)
            assert diff == 3

        def test_exclusive_of_end_date():
            start_dt = datetime(2023, 12, 29, 18, 0, 55)
            end_dt = datetime(2023, 12, 31, 1, 57, 19)
            diff = utils.get_num_days_from_to(start_dt, end_dt, False)
            assert diff == 2

        def test_same_day_inclusive_of_end():
            start_dt = datetime(2023, 12, 29, 1, 57, 19)
            end_dt = datetime(2023, 12, 29, 18, 0, 55)
            diff = utils.get_num_days_from_to(start_dt, end_dt)
            assert diff == 1

        def test_same_day_exclusive_of_end():
            start_dt = datetime(2023, 12, 29, 1, 57, 19)
            end_dt = datetime(2023, 12, 29, 18, 0, 55)
            diff = utils.get_num_days_from_to(start_dt, end_dt, False)
            assert diff == 0

        test_inclusive_of_end_date()
        test_exclusive_of_end_date()
        test_same_day_inclusive_of_end()
        test_same_day_exclusive_of_end()

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

    def test_add_positive_num_of_intervals(self):
        def test_for_day_intervals():
            new_dt = utils.add_interval("2023-10-05", "daily", 9)
            assert new_dt == "2023-10-14"

        def test_for_week_intervals():
            new_dt = utils.add_interval("2023-10-05", "weekly", 4)
            assert new_dt == "2023-11-02"

        test_for_day_intervals()
        test_for_week_intervals()

    def test_add_negative_num_of_intervals(self):
        def test_for_day_intervals():
            new_dt = utils.add_interval("2023-10-05", "daily", -9)
            assert new_dt == "2023-09-26"

        def test_for_week_intervals():
            new_dt = utils.add_interval("2023-10-05", "weekly", -1)
            assert new_dt == "2023-09-28"

        test_for_day_intervals()
        test_for_week_intervals()

    def test_add_zero_num_of_intervals(self):
        def test_for_day_intervals():
            new_dt = utils.add_interval("2023-10-05", "daily", 0)
            assert new_dt == "2023-10-05"

        def test_for_week_intervals():
            new_dt = utils.add_interval("2023-10-05", "weekly", 0)
            assert new_dt == "2023-10-05"

        test_for_day_intervals()
        test_for_week_intervals()

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

        setup_method()
        test_no_activities()
        test_grouping_by_day()
        test_grouping_by_week()
        teardown_method()

    def test_grouping_with_date_filters(self):
        def setup_method():
            db.connect("test.db")
            db.setup_tables()

        def teardown_method():
            db.remove_tables()
            db.disconnect()

        def test_grouping_by_day():
            habit = Habit("Practise piano", "daily", "2023-05-28 18:15:32")
            habit.perform("2023-05-29 20:12:12")
            habit.perform("2023-05-29 22:05:56")
            habit.perform("2023-06-03 01:37:05")
            habit.perform("2023-06-05 12:03:59")
            habit.perform("2023-06-05 08:57:00")
            habit.perform("2023-06-05 21:49:22")
            habit.perform("2023-06-11 17:33:45")

            # start date only
            grouped_by_dt = utils.group_activities_by_performance_period(
                habit.get_activities(),
                habit.get_recurrence(),
                utils.to_datetime("2023-06-04 15:34:12"),
            )
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 2
            assert len(grouped_by_dt["2023-06-05"]) == 3
            assert len(grouped_by_dt["2023-06-11"]) == 1

            # end date only
            grouped_by_dt = utils.group_activities_by_performance_period(
                habit.get_activities(),
                habit.get_recurrence(),
                end_date=utils.to_datetime("2023-06-04 15:34:12"),
            )
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 2
            assert len(grouped_by_dt["2023-05-29"]) == 2
            assert len(grouped_by_dt["2023-06-03"]) == 1

            # start date and end date
            grouped_by_dt = utils.group_activities_by_performance_period(
                habit.get_activities(),
                habit.get_recurrence(),
                utils.to_datetime("2023-06-04 00:00:00"),
                utils.to_datetime("2023-06-10 23:59:59"),
            )
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 1
            assert len(grouped_by_dt["2023-06-05"]) == 3

        def test_grouping_by_week():
            habit = Habit("Water plants", "weekly", "2023-05-28 18:15:32")
            habit.perform("2023-05-29 20:12:12")
            habit.perform("2023-06-03 22:05:56")
            # -----------------------------------
            habit.perform("2023-06-05 01:37:05")
            habit.perform("2023-06-10 12:03:59")
            habit.perform("2023-06-11 08:57:00")
            # -----------------------------------
            habit.perform("2023-06-29 21:49:22")
            habit.perform("2023-07-02 17:33:45")

            # start date only
            grouped_by_dt = utils.group_activities_by_performance_period(
                habit.get_activities(),
                habit.get_recurrence(),
                utils.to_datetime("2023-06-04 15:34:12"),
            )
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 2
            assert len(grouped_by_dt["2023-06-05"]) == 3
            assert len(grouped_by_dt["2023-06-26"]) == 2

            # end date only
            grouped_by_dt = utils.group_activities_by_performance_period(
                habit.get_activities(),
                habit.get_recurrence(),
                end_date=utils.to_datetime("2023-06-04 15:34:12"),
            )
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 1
            assert len(grouped_by_dt["2023-05-29"]) == 2

            # start date and end date
            grouped_by_dt = utils.group_activities_by_performance_period(
                habit.get_activities(),
                habit.get_recurrence(),
                utils.to_datetime("2023-06-10 15:00:00"),
                utils.to_datetime("2023-06-30 23:59:59"),
            )
            assert grouped_by_dt is not None
            assert len(grouped_by_dt.keys()) == 2
            assert len(grouped_by_dt["2023-06-05"]) == 1
            assert len(grouped_by_dt["2023-06-26"]) == 1

        setup_method()
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

        teardown_method()

    def test_get_last_week_date_range(self):
        (start, end) = utils.get_last_week_date_range(datetime(2024, 1, 3, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2023-12-28 00:00:00"
        assert end_text == "2024-01-03 14:53:21"

    def test_get_last_month_date_range_straightforward(self):
        (start, end) = utils.get_last_month_date_range(datetime(2024, 3, 28, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2024-02-29 00:00:00"
        assert end_text == "2024-03-28 14:53:21"

    def test_get_last_month_date_range_previous_year(self):
        (start, end) = utils.get_last_month_date_range(datetime(2024, 1, 3, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2023-12-04 00:00:00"
        assert end_text == "2024-01-03 14:53:21"

    def test_get_last_month_date_range_special_january_case(self):
        (start, end) = utils.get_last_month_date_range(datetime(2024, 1, 31, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2024-01-01 00:00:00"
        assert end_text == "2024-01-31 14:53:21"

    def test_get_last_month_date_range_longer_month(self):
        (start, end) = utils.get_last_month_date_range(datetime(2024, 3, 30, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2024-03-01 00:00:00"
        assert end_text == "2024-03-30 14:53:21"

    def test_get_last_6_months_date_range_straightforward(self):
        (start, end) = utils.get_last_6_months_date_range(datetime(2024, 10, 3, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2024-04-04 00:00:00"
        assert end_text == "2024-10-03 14:53:21"

    def test_get_last_6_months_date_range_previous_year(self):
        (start, end) = utils.get_last_6_months_date_range(datetime(2024, 4, 3, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2023-10-04 00:00:00"
        assert end_text == "2024-04-03 14:53:21"

    def test_get_last_6_months_date_range_longer_month(self):
        (start, end) = utils.get_last_6_months_date_range(datetime(2024, 8, 29, 14, 53, 21))
        start_text = datetime.strftime(start, "%Y-%m-%d %H:%M:%S")
        end_text = datetime.strftime(end, "%Y-%m-%d %H:%M:%S")
        assert start_text == "2024-03-01 00:00:00"
        assert end_text == "2024-08-29 14:53:21"

