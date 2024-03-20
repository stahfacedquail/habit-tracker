from modules import db
from modules.utils import to_datetime
from classes.habit import Habit


class TestStreaksForWeeklyHabits:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_multiple_streaks(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")    # Week 1    -- start Streak 1
        habit.perform("2023-09-21 16:42:11")    # Week 1
        habit.perform("2023-09-28 21:30:31")    # Week 2    -- end Streak 1
        habit.perform("2023-10-22 20:30:47")    # Week 5
        habit.perform("2023-11-03 20:57:17")    # Week 7
        habit.perform("2023-11-20 18:11:06")    # Week 10
        habit.perform("2023-11-24 19:06:56")    # Week 10
        habit.perform("2023-12-05 20:51:22")    # Week 12
        habit.perform("2023-12-09 20:47:20")    # Week 12
        habit.perform("2024-01-06 17:39:39")    # Week 16   -- start Streak 2
        habit.perform("2024-01-10 16:15:50")    # Week 17
        habit.perform("2024-01-21 21:42:03")    # Week 18   -- end Streak 2
        habit.perform("2024-01-31 19:23:37")    # Week 20
        habit.perform("2024-02-28 17:17:45")    # Week 24

        streaks = habit.get_all_streaks()
        assert len(streaks) == 2

        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2024-01-06 17:39:39")
        assert streak_1["end"] == to_datetime("2024-01-21 21:42:03")
        assert streak_1["length"] == 3
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-09-18 16:20:30")
        assert streak_2["end"] == to_datetime("2023-09-28 21:30:31")
        assert streak_2["length"] == 2

    def test_streak_at_end_of_list(self):
        habit = Habit("Phone parents", "weekly", "2023-12-05 18:51:24")
        habit.perform("2023-12-06 16:59:44")    # Week 1
        habit.perform("2023-12-27 16:46:09")    # Week 4    -- start Streak 1
        habit.perform("2024-01-02 19:16:37")    # Week 5
        habit.perform("2024-01-10 20:10:43")    # Week 6
        habit.perform("2024-01-21 19:22:15")    # Week 7    -- end Streak 1

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-12-27 16:46:09")
        assert streak_1["end"] == to_datetime("2024-01-21 19:22:15")
        assert streak_1["length"] == 4

    def test_streak_at_beginning_of_list(self):
        habit = Habit("Phone parents", "weekly", "2023-12-05 18:51:24")
        habit.perform("2023-12-06 16:59:44")    # Week 1    -- start Streak 1
        habit.perform("2023-12-11 16:46:09")    # Week 2
        habit.perform("2023-12-23 19:16:37")    # Week 3    -- end Streak 1
        habit.perform("2024-01-10 20:10:43")    # Week 6
        habit.perform("2024-01-25 19:22:15")    # Week 8

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-12-06 16:59:44")
        assert streak_1["end"] == to_datetime("2023-12-23 19:16:37")
        assert streak_1["length"] == 3

    def test_streak_with_multiple_performances_per_week_at_beginning_of_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")    # Week 1    -- start Streak 1
        habit.perform("2023-09-21 16:42:11")    # Week 1
        habit.perform("2023-09-21 21:30:31")    # Week 1
        habit.perform("2023-09-23 20:30:47")    # Week 1
        habit.perform("2023-09-27 05:16:00")    # Week 2    -- end Streak 1
        habit.perform("2023-10-22 13:00:01")    # Week 5

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1

        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-09-18 16:20:30")
        assert streak_1["end"] == to_datetime("2023-09-27 05:16:00")
        assert streak_1["length"] == 2

    def test_streak_with_multiple_performances_per_week_at_end_of_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")    # Week 1
        habit.perform("2023-10-04 16:20:30")    # Week 3    -- start Streak 1
        habit.perform("2023-10-10 20:30:47")    # Week 4
        habit.perform("2023-10-18 05:16:00")    # Week 5
        habit.perform("2023-10-20 13:00:01")    # Week 5
        habit.perform("2023-10-21 20:57:17")    # Week 5    -- end Streak 1

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1

        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-10-04 16:20:30")
        assert streak_1["end"] == to_datetime("2023-10-21 20:57:17")
        assert streak_1["length"] == 3

    def test_streak_with_multiple_performances_per_week_in_middle_of_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")    # Week 1
        habit.perform("2023-10-03 16:42:11")    # Week 3
        habit.perform("2023-10-24 21:30:31")    # Week 6    -- start Streak 1
        habit.perform("2023-10-31 20:30:47")    # Week 7
        habit.perform("2023-11-03 05:16:00")    # Week 7
        habit.perform("2023-11-03 13:00:01")    # Week 7
        habit.perform("2023-11-06 15:19:33")    # Week 8
        habit.perform("2023-11-11 22:28:37")    # Week 8    -- end Streak 1
        habit.perform("2023-12-25 20:57:17")    # Week 11

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1

        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-10-24 21:30:31")
        assert streak_1["end"] == to_datetime("2023-11-11 22:28:37")
        assert streak_1["length"] == 3

    def test_streak_with_multiple_performances_per_week_not_part_of_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-10-18 16:20:30")    # Week 1    -- start Streak 1
        habit.perform("2023-10-21 16:42:11")    # Week 1
        habit.perform("2023-10-24 21:30:31")    # Week 2    -- end Streak 1
        habit.perform("2023-11-06 20:30:47")    # Week 4
        habit.perform("2023-11-07 05:16:00")    # Week 4
        habit.perform("2023-11-10 13:00:01")    # Week 4

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1

        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-10-18 16:20:30")
        assert streak_1["end"] == to_datetime("2023-10-24 21:30:31")
        assert streak_1["length"] == 2

    def test_whole_period_is_a_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-18 16:20:30")    # Week 1    -- start Streak 1
        habit.perform("2023-09-27 16:42:11")    # Week 2
        habit.perform("2023-10-03 21:30:31")    # Week 3
        habit.perform("2023-10-14 20:30:47")    # Week 4
        habit.perform("2023-10-16 05:16:00")    # Week 5    -- end Streak 1

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1

        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-09-18 16:20:30")
        assert streak_1["end"] == to_datetime("2023-10-16 05:16:00")
        assert streak_1["length"] == 5

    # 4. test no streaks
    def test_no_streaks(self):
        habit = Habit("Phone parents", "weekly", "2023-09-14 19:01:16")
        habit.perform("2023-09-16 19:44:47")    # Week 1
        habit.perform("2023-10-01 19:43:34")    # Week 3
        habit.perform("2023-10-30 20:09:22")    # Week 8

        streaks = habit.get_all_streaks()
        assert len(streaks) == 0

    def test_no_activities(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 18:15:43")
        streaks = habit.get_all_streaks()
        assert streaks is not None
        assert len(streaks) == 0

    def test_sorting(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:00:43")
        habit.perform("2023-05-29 11:23:45")    # Week 1    -- start Streak 1
        habit.perform("2023-06-06 08:17:54")    # Week 2    -- end Streak 1
        habit.perform("2023-06-27 17:18:19")    # Week 5    -- start Streak 2
        habit.perform("2023-06-30 21:34:45")    # Week 5
        habit.perform("2023-07-06 18:29:54")    # Week 6
        habit.perform("2023-07-11 11:15:43")    # Week 7
        habit.perform("2023-07-20 15:00:29")    # Week 8
        habit.perform("2023-07-29 15:00:29")    # Week 9    -- end Streak 2
        habit.perform("2023-08-20 14:55:21")    # Week 12
        habit.perform("2023-09-28 23:14:11")    # Week 18   -- start Streak 3
        habit.perform("2023-10-04 16:57:12")    # Week 19
        habit.perform("2023-10-15 12:38:47")    # Week 20   -- end Streak 3
        habit.perform("2023-10-24 20:38:02")    # Week 22

        # default sort: by date, descending
        streaks = habit.get_all_streaks()
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-09-28 23:14:11")
        assert streak_1["end"] == to_datetime("2023-10-15 12:38:47")
        assert streak_1["length"] == 3
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-06-27 17:18:19")
        assert streak_2["end"] == to_datetime("2023-07-29 15:00:29")
        assert streak_2["length"] == 5
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_3["end"] == to_datetime("2023-06-06 08:17:54")
        assert streak_3["length"] == 2

        streaks = habit.get_all_streaks("date", "asc")
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_1["end"] == to_datetime("2023-06-06 08:17:54")
        assert streak_1["length"] == 2
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-06-27 17:18:19")
        assert streak_2["end"] == to_datetime("2023-07-29 15:00:29")
        assert streak_2["length"] == 5
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-09-28 23:14:11")
        assert streak_3["end"] == to_datetime("2023-10-15 12:38:47")
        assert streak_3["length"] == 3

        streaks = habit.get_all_streaks("length", "desc")
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-06-27 17:18:19")
        assert streak_1["end"] == to_datetime("2023-07-29 15:00:29")
        assert streak_1["length"] == 5
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-09-28 23:14:11")
        assert streak_2["end"] == to_datetime("2023-10-15 12:38:47")
        assert streak_2["length"] == 3
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_3["end"] == to_datetime("2023-06-06 08:17:54")
        assert streak_3["length"] == 2

        streaks = habit.get_all_streaks("length", "asc")
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_1["end"] == to_datetime("2023-06-06 08:17:54")
        assert streak_1["length"] == 2
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-09-28 23:14:11")
        assert streak_2["end"] == to_datetime("2023-10-15 12:38:47")
        assert streak_2["length"] == 3
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-06-27 17:18:19")
        assert streak_3["end"] == to_datetime("2023-07-29 15:00:29")
        assert streak_3["length"] == 5


    def teardown_method(self):
        db.remove_tables()
        db.disconnect()