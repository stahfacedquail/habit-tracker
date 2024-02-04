import db
import utils
from classes.habit import Habit


class TestStreaksForDailyHabits:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_many_streaks(self):
        habit = Habit("Practise piano", "daily", "2023-05-24 18:15:43")
        habit.perform("2023-05-25 16:00:12")
        habit.perform("2023-05-28 18:15:55")
        habit.perform("2023-05-29 19:13:14")
        habit.perform("2023-05-30 16:57:59")
        habit.perform("2023-06-02 19:29:09")
        habit.perform("2023-06-03 18:47:42")
        habit.perform("2023-06-04 20:30:04")
        habit.perform("2023-06-05 17:25:33")
        habit.perform("2023-06-06 18:59:13")
        habit.perform("2023-06-07 20:22:21")
        habit.perform("2023-06-08 18:53:14")
        habit.perform("2023-06-10 18:24:59")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 2
        streak_1 = streaks[0]
        assert streak_1["start"] == utils.to_datetime("2023-06-02 19:29:09")
        assert streak_1["end"] == utils.to_datetime("2023-06-08 18:53:14")
        assert streak_1["length"] == 7
        streak_2 = streaks[1]
        assert streak_2["start"] == utils.to_datetime("2023-05-28 18:15:55")
        assert streak_2["end"] == utils.to_datetime("2023-05-30 16:57:59")
        assert streak_2["length"] == 3

    def test_streak_at_end_of_list(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-06-17 16:48:06")
        habit.perform("2023-06-21 18:59:43")
        habit.perform("2023-06-22 20:22:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak = streaks[0]
        assert streak["start"] == utils.to_datetime("2023-06-21 18:59:43")
        assert streak["end"] == utils.to_datetime("2023-06-22 20:22:13")
        assert streak["length"] == 2

    def test_streak_with_multiple_performances_per_day(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-05-30 12:00:42")
        habit.perform("2023-06-02 19:29:09")
        habit.perform("2023-06-03 14:47:42")
        habit.perform("2023-06-03 21:49:11")
        habit.perform("2023-06-04 13:30:04")
        habit.perform("2023-06-04 17:09:19")
        habit.perform("2023-06-05 13:25:33")
        habit.perform("2023-06-05 15:13:30")
        habit.perform("2023-06-05 22:58:46")
        habit.perform("2023-06-06 18:59:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == utils.to_datetime("2023-06-02 19:29:09")
        assert streak_1["end"] == utils.to_datetime("2023-06-06 18:59:13")
        assert streak_1["length"] == 5

    def test_no_streaks(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-06-02 19:29:09")
        habit.perform("2023-06-04 13:30:04")
        habit.perform("2023-06-07 22:58:46")
        habit.perform("2023-06-23 18:59:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 0

    def test_no_activities(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        streaks = habit.get_all_streaks()
        assert streaks is not None
        assert len(streaks) == 0

    def test_sorting_on_date_ascending(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:00:43")
        habit.perform("2023-05-29 11:23:45")
        habit.perform("2023-05-30 08:17:54")
        habit.perform("2023-06-17 17:18:19")
        habit.perform("2023-06-18 21:34:45")
        habit.perform("2023-06-19 18:29:54")
        habit.perform("2023-06-20 11:15:43")

        streaks = habit.get_all_streaks("date", "asc")
        streak_1 = streaks[0]
        assert streak_1["start"] == utils.to_datetime("2023-05-29 11:23:45")
        assert streak_1["end"] == utils.to_datetime("2023-05-30 08:17:54")
        assert streak_1["length"] == 2
        streak_2 = streaks[1]
        assert streak_2["start"] == utils.to_datetime("2023-06-17 17:18:19")
        assert streak_2["end"] == utils.to_datetime("2023-06-20 11:15:43")
        assert streak_2["length"] == 4

    def test_sorting_on_length_descending(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:00:43")
        habit.perform("2023-05-29 11:23:45")
        habit.perform("2023-06-06 08:17:54")
        habit.perform("2023-06-27 17:18:19")
        habit.perform("2023-06-30 21:34:45")
        habit.perform("2023-07-06 18:29:54")
        habit.perform("2023-07-11 11:15:43")

        streaks = habit.get_all_streaks("length", "desc")
        streak_1 = streaks[0]
        assert streak_1["start"] == utils.to_datetime("2023-06-27 17:18:19")
        assert streak_1["end"] == utils.to_datetime("2023-07-11 11:15:43")
        assert streak_1["length"] == 3
        streak_2 = streaks[1]
        assert streak_2["start"] == utils.to_datetime("2023-05-29 11:23:45")
        assert streak_2["end"] == utils.to_datetime("2023-06-06 08:17:54")
        assert streak_2["length"] == 2

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()


class TestStreaksForWeeklyHabits:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_streak_at_end_of_list(self):
        # Calendar:
        # DECEMBER
        #   Mo      Tu      We      Th      Fr      Sa      Su
        #                  (06)     07      08      09      10  [*]
        #   11      12      13      14      15      16      17   -
        #   18      19      20      21      22      23      24   -
        #   25      26     (27)     28      29      30      31  [*]
        # JANUARY
        #   01     (02)     03      04      05      06      07  [*]
        #   08      09     (10)     11      12      13      14  [*]
        #   15      16      17      18      19      20     (21) [*]
        habit = Habit("Phone parents", "weekly", "2023-12-05 18:51:24")
        habit.perform("2023-12-06 16:59:44")
        habit.perform("2023-12-27 16:46:09")
        habit.perform("2024-01-02 19:16:37")
        habit.perform("2024-01-10 20:10:43")
        habit.perform("2024-01-21 19:22:15")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == utils.to_datetime("2023-12-27 16:46:09")
        assert streak_1["end"] == utils.to_datetime("2024-01-21 19:22:15")
        assert streak_1["length"] == 4

    # 2. test more than one streak in list
    def test_multiple_streaks(self):
        # Calendar:
        # SEPTEMBER
        #   Mo      Tu      We      Th      Fr      Sa      Su
        #  (18)     19      20     (21)     22      23      24      [*]
        #   25      26      27     (28)     29      30      --  |
        # OCTOBER                                               |   [*] one week
        #   --      --      --      --      --      --      01  |
        #   02      03      04      05      06      07      08       -
        #   09      10      11      12      13      14      15       -
        #   16      17      18      19      20      21     (22)     [*]
        #   23      24      25      26      27      28      29       -
        #   30      31      --      --      --      --      --  |
        # NOVEMBER                                              |   [*] one week
        #   --      --      01      02     (03)     04      05  |
        #   06      07      08      09      10      11      12       -
        #   13      14      15      16      17      18      19       -
        #  (20)     21      22      23     (24)     25      26      [*]
        #   27      28      29      30      --      --      --  |
        # DECEMBER                                              |    - one week
        #   --      --      --      --      01      02      03  |
        #   04     (05)     06      07      08     (09)     10      [*]
        #   11      12      13      14      15      16      17       -
        #   18      19      20      21      22      23      24       -
        #   25      26      27      28      29      30      31       -
        # JANUARY
        #   01      02      03      04      05     (06)     07      [*]
        #   08      09      10      11      12     (13)     14      [*]
        #   15      16      17      18      19     (20)     21      [*]
        #   22      23      24      25      26      27      28       -
        #   29      30     (31)     --      --      --      --  |
        # FEBRUARY                                              |   [*] one week
        #   --      --      --      01      02      03      04  |
        #   05      06      07      08      09      10      11       -
        #   12      13      14      15      16      17      18       -
        #   19      20      21      22      23      24      25       -
        #   26      27     (28)                                     [*]
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")
        habit.perform("2023-09-21 16:42:11")
        habit.perform("2023-09-28 21:30:31")
        habit.perform("2023-10-22 20:30:47")
        habit.perform("2023-11-03 20:57:17")
        habit.perform("2023-11-20 18:11:06")
        habit.perform("2023-11-24 19:06:56")
        habit.perform("2023-12-05 20:51:22")
        habit.perform("2023-12-09 20:47:20")
        habit.perform("2024-01-06 17:39:39")
        habit.perform("2024-01-13 16:15:50")
        habit.perform("2024-01-20 21:42:03")
        habit.perform("2024-01-31 19:23:37")
        habit.perform("2024-02-28 17:17:45")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 2

        streak_1 = streaks[0]
        streak_2 = streaks[1]
        assert streak_1["start"] == utils.to_datetime("2024-01-06 17:39:39")
        assert streak_1["end"] == utils.to_datetime("2024-01-20 21:42:03")
        assert streak_1["length"] == 3
        assert streak_2["start"] == utils.to_datetime("2023-09-18 16:20:30")
        assert streak_2["end"] == utils.to_datetime("2023-09-28 21:30:31")
        assert streak_2["length"] == 2

    # 3. test streak when multiple performances per week
    def test_multiple_performances_per_week(self):
        # Calendar:
        # SEPTEMBER
        #   Mo      Tu      We      Th      Fr      Sa      Su
        #  (18)     19      20    ((21))    22     (23)     24      [*]
        #   25      26   (((27)))   28      29      30              [*]
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")
        habit.perform("2023-09-21 16:42:11")
        habit.perform("2023-09-21 21:30:31")
        habit.perform("2023-09-23 20:30:47")
        habit.perform("2023-09-27 05:16:00")
        habit.perform("2023-09-27 13:00:01")
        habit.perform("2023-09-27 20:57:17")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1

        streak_1 = streaks[0]
        assert streak_1["start"] == utils.to_datetime("2023-09-18 16:20:30")
        assert streak_1["end"] == utils.to_datetime("2023-09-27 20:57:17")
        assert streak_1["length"] == 2

    # 4. test no streaks
    def test_no_streaks(self):
        # Calendar:
        # SEPTEMBER
        #   Mo      Tu      We      Th      Fr      Sa      Su
        #   11      12      13      14      15     (16)     17      [*]
        #   18      19      20      21      22      23      24       -
        #   25      26      27      28      29      30      --  |
        # OCTOBER                                               |   [*] one week
        #   --      --      --      --      --      --     (01) |
        #   02      03      04      05      06      07      08       -
        #   09      10      11      12      13      14      15       -
        #   16      17      18      19      20      21      22       -
        #   23      24      25      26      27      28      29       -
        #  (30)     31      --      --      --      --      --      [*]
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-16 19:44:47")
        habit.perform("2023-10-01 19:43:34")
        habit.perform("2023-10-30 20:09:22")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 0

    def test_no_activities(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 18:15:43")
        streaks = habit.get_all_streaks()
        assert streaks is not None
        assert len(streaks) == 0

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()


class TestLatestStreak:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_no_activities(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 09:22:57")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] is None
        assert current_streak["end"] is None
        assert current_streak["length"] == 0
        assert current_streak["is_current"] is None
        assert current_streak["can_extend_today"] is None

    def test_one_period_streak(self):
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 09:21:57")
            habit.perform("2023-05-31 11:17:49")
            habit.perform("2023-06-15 17:00:34")
            habit.perform("2023-06-17 00:55:21")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-06-17 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-06-17 00:55:21")
            assert current_streak["length"] == 1

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 09:21:57")
            habit.perform("2023-05-31 10:17:49")
            habit.perform("2023-06-15 18:00:34")
            habit.perform("2023-06-28 00:55:21")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-06-28 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-06-28 00:55:21")
            assert current_streak["length"] == 1

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_one_period_streak_with_multiple_performances_per_period(self):
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-05-31 11:17:49")
            habit.perform("2023-05-31 17:00:34")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-05-31 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-05-31 17:00:34")
            assert current_streak["length"] == 1

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-06-03 11:17:49")
            habit.perform("2023-06-03 12:06:52")
            habit.perform("2023-06-04 17:00:34")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-05-31 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-06-04 17:00:34")
            assert current_streak["length"] == 1

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_multi_period_streak(self):
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-06-01 11:17:49")
            habit.perform("2023-06-02 17:00:34")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-05-31 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-06-02 17:00:34")
            assert current_streak["length"] == 3

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-06-07 11:17:49")
            habit.perform("2023-06-12 17:00:34")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-05-31 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-06-12 17:00:34")
            assert current_streak["length"] == 3

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_multi_period_streak_with_multiple_performances_per_period(self):
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:25")
            habit.perform("2023-05-31 14:12:02")
            habit.perform("2023-05-31 18:23:48")
            habit.perform("2023-06-01 11:05:25")
            habit.perform("2023-06-01 13:17:16")
            habit.perform("2023-06-12 09:00:42")
            habit.perform("2023-06-12 19:52:27")
            habit.perform("2023-06-15 00:19:04")
            habit.perform("2023-06-16 11:25:31")
            habit.perform("2023-06-16 17:08:51")
            habit.perform("2023-06-17 15:49:20")
            habit.perform("2023-06-17 20:12:49")
            habit.perform("2023-06-17 23:36:26")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-06-15 00:19:04")
            assert current_streak["end"] == utils.to_datetime("2023-06-17 23:36:26")
            assert current_streak["length"] == 3

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-06-06 11:17:49")
            habit.perform("2023-06-07 23:10:35")
            habit.perform("2023-06-12 17:00:34")
            habit.perform("2023-06-15 22:40:24")
            habit.perform("2023-06-16 21:52:51")
            habit.perform("2023-06-30 14:18:32")
            habit.perform("2023-06-30 20:19:39")
            habit.perform("2023-07-01 19:56:15")
            habit.perform("2023-07-03 16:42:58")
            habit.perform("2023-07-10 07:29:36")
            habit.perform("2023-07-10 22:11:33")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-06-30 14:18:32")
            assert current_streak["end"] == utils.to_datetime("2023-07-10 22:11:33")
            assert current_streak["length"] == 3

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_with_many_streaks(self):
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-06-01 11:17:49")
            habit.perform("2023-06-12 17:00:34")
            habit.perform("2023-06-15 00:55:21")
            habit.perform("2023-06-16 11:17:49")
            habit.perform("2023-06-17 15:23:44")
            habit.perform("2023-06-22 16:03:57")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-06-22 16:03:57")
            assert current_streak["end"] == utils.to_datetime("2023-06-22 16:03:57")
            assert current_streak["length"] == 1

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
            habit.perform("2023-05-31 00:55:21")
            habit.perform("2023-06-07 11:17:49")
            habit.perform("2023-06-12 17:00:34")
            habit.perform("2023-06-30 00:55:21")
            habit.perform("2023-07-06 11:17:49")
            current_streak = habit.get_latest_streak()
            assert current_streak is not None
            assert current_streak["start"] == utils.to_datetime("2023-06-30 00:55:21")
            assert current_streak["end"] == utils.to_datetime("2023-07-06 11:17:49")
            assert current_streak["length"] == 2

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_latest_streak_is_old(self):
        """
        If today can only start a fresh streak, the last streak that was achieved should be returned.
        """
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:03:25")
            habit.perform("2023-05-29 18:15:36")
            habit.perform("2023-05-30 20:03:45")
            habit.perform("2023-05-31 19:12:46")
            latest_streak = habit.get_latest_streak(utils.to_datetime("2023-06-05 15:00:00"))
            assert latest_streak["start"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["end"] == utils.to_datetime("2023-05-31 19:12:46")
            assert latest_streak["is_current"] is False
            assert latest_streak["can_extend_today"] is False

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:03:25")
            habit.perform("2023-05-29 18:15:36")
            latest_streak = habit.get_latest_streak(utils.to_datetime("2023-06-12 15:00:00"))
            assert latest_streak["start"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["end"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["is_current"] is False
            assert latest_streak["can_extend_today"] is False

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_latest_streak_is_recent(self):
        """
        If today could extend a streak, the latest streak should be returned, along with an indication that the
        "window" to extend the streak is still open.
        """
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:03:25")
            habit.perform("2023-05-29 18:15:36")
            habit.perform("2023-05-30 20:03:45")
            habit.perform("2023-05-31 19:12:46")
            latest_streak = habit.get_latest_streak(utils.to_datetime("2023-06-01 15:00:00"))
            assert latest_streak["start"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["end"] == utils.to_datetime("2023-05-31 19:12:46")
            assert latest_streak["is_current"] is True
            assert latest_streak["can_extend_today"] is True

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:03:25")
            habit.perform("2023-05-29 18:15:36")
            latest_streak = habit.get_latest_streak(utils.to_datetime("2023-06-07 15:00:00"))
            assert latest_streak["start"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["end"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["is_current"] is True
            assert latest_streak["can_extend_today"] is True

        test_for_daily_habit()
        test_for_weekly_habit()

    def test_latest_streak_is_current(self):
        """
        If today is part of an ongoing streak, the details of the streak should be returned, as well as an indication
        that today falls within the period range of the streak.
        :return:
        """
        def test_for_daily_habit():
            habit = Habit("Practise piano", "daily", "2023-05-28 19:03:25")
            habit.perform("2023-05-29 18:15:36")
            habit.perform("2023-05-30 20:03:45")
            habit.perform("2023-05-31 19:12:46")
            latest_streak = habit.get_latest_streak(utils.to_datetime("2023-05-31 20:00:00"))
            assert latest_streak["start"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["end"] == utils.to_datetime("2023-05-31 19:12:46")
            assert latest_streak["is_current"] is True
            assert latest_streak["can_extend_today"] is False

        def test_for_weekly_habit():
            habit = Habit("Phone parents", "weekly", "2023-05-28 19:03:25")
            habit.perform("2023-05-29 18:15:36")
            latest_streak = habit.get_latest_streak(utils.to_datetime("2023-06-01 15:00:00"))
            assert latest_streak["start"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["end"] == utils.to_datetime("2023-05-29 18:15:36")
            assert latest_streak["is_current"] is True
            assert latest_streak["can_extend_today"] is False

        test_for_daily_habit()
        test_for_weekly_habit()

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
