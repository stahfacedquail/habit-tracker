from modules import db
from modules.utils import to_datetime
from classes.habit import Habit


class TestStreaksForDailyHabits:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_multiple_streaks(self):
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
        assert streak_1["start"] == to_datetime("2023-06-02 19:29:09")
        assert streak_1["end"] == to_datetime("2023-06-08 18:53:14")
        assert streak_1["length"] == 7
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-05-28 18:15:55")
        assert streak_2["end"] == to_datetime("2023-05-30 16:57:59")
        assert streak_2["length"] == 3

    def test_streak_at_end_of_list(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-06-17 16:48:06")
        habit.perform("2023-06-21 18:59:43")
        habit.perform("2023-06-22 20:22:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak = streaks[0]
        assert streak["start"] == to_datetime("2023-06-21 18:59:43")
        assert streak["end"] == to_datetime("2023-06-22 20:22:13")
        assert streak["length"] == 2

    def test_streak_at_beginning_of_list(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-06-17 16:48:06")
        habit.perform("2023-06-18 18:59:43")
        habit.perform("2023-06-19 20:18:32")
        habit.perform("2023-06-22 20:22:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak = streaks[0]
        assert streak["start"] == to_datetime("2023-06-17 16:48:06")
        assert streak["end"] == to_datetime("2023-06-19 20:18:32")
        assert streak["length"] == 3

    def test_streak_with_multiple_performances_per_day_at_beginning_of_streak(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-05-30 12:00:42")
        habit.perform("2023-05-30 16:23:11")
        habit.perform("2023-05-31 22:58:35")
        habit.perform("2023-06-01 19:29:09")
        habit.perform("2023-06-02 14:47:42")
        habit.perform("2023-06-06 18:59:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-30 05:01:59")
        assert streak_1["end"] == to_datetime("2023-06-02 14:47:42")
        assert streak_1["length"] == 4

    def test_streak_with_multiple_performances_per_day_at_end_of_streak(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-28 18:25:33")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-05-31 12:00:42")
        habit.perform("2023-06-01 05:29:09")
        habit.perform("2023-06-01 14:47:42")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-30 05:01:59")
        assert streak_1["end"] == to_datetime("2023-06-01 14:47:42")
        assert streak_1["length"] == 3

    def test_streak_with_multiple_performances_per_day_in_middle_of_streak(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-29 05:01:59")
        habit.perform("2023-06-01 12:00:42")
        habit.perform("2023-06-02 06:29:09")
        habit.perform("2023-06-02 14:47:42")
        habit.perform("2023-06-02 21:49:11")
        habit.perform("2023-06-03 13:30:04")
        habit.perform("2023-06-04 17:09:19")
        habit.perform("2023-06-08 12:43:01")
        habit.perform("2023-06-10 15:32:26")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-06-01 12:00:42")
        assert streak_1["end"] == to_datetime("2023-06-04 17:09:19")
        assert streak_1["length"] == 4

    def test_streak_with_multiple_performances_per_day_not_part_of_streak(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-05-31 12:00:42")
        habit.perform("2023-06-02 06:29:09")
        habit.perform("2023-06-02 08:47:42")
        habit.perform("2023-06-02 13:49:11")
        habit.perform("2023-06-02 17:30:04")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-30 05:01:59")
        assert streak_1["end"] == to_datetime("2023-05-31 12:00:42")
        assert streak_1["length"] == 2

    def test_whole_period_is_a_streak(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-05-31 12:00:42")
        habit.perform("2023-06-01 06:29:09")
        habit.perform("2023-06-02 08:47:42")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-30 05:01:59")
        assert streak_1["end"] == to_datetime("2023-06-02 08:47:42")
        assert streak_1["length"] == 4

    def test_no_streaks(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-05-30 05:01:59")
        habit.perform("2023-06-02 19:29:09")
        habit.perform("2023-06-04 13:30:04")
        habit.perform("2023-06-07 22:58:46")
        habit.perform("2023-06-23 18:59:13")

        streaks = habit.get_all_streaks()
        assert streaks is not None
        assert len(streaks) == 0

    def test_no_activities(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        streaks = habit.get_all_streaks()
        assert streaks is not None
        assert len(streaks) == 0

    def test_sorting(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:00:43")
        habit.perform("2023-05-29 11:23:45")  # start streak 1
        habit.perform("2023-05-30 08:17:54")  # end streak 1
        habit.perform("2023-06-17 17:18:19")  # start streak 2
        habit.perform("2023-06-18 21:34:45")
        habit.perform("2023-06-19 18:29:54")
        habit.perform("2023-06-20 11:15:43")  # end streak 2
        habit.perform("2023-06-25 19:54:07")  # start streak 3
        habit.perform("2023-06-26 15:29:33")
        habit.perform("2023-06-27 07:10:58")
        habit.perform("2023-06-27 19:00:28")  # end streak 3

        # default sorting (by date, descending)
        streaks = habit.get_all_streaks()
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-06-25 19:54:07")
        assert streak_1["end"] == to_datetime("2023-06-27 19:00:28")
        assert streak_1["length"] == 3
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-06-17 17:18:19")
        assert streak_2["end"] == to_datetime("2023-06-20 11:15:43")
        assert streak_2["length"] == 4
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_3["end"] == to_datetime("2023-05-30 08:17:54")
        assert streak_3["length"] == 2

        # sort by date, ascending
        streaks = habit.get_all_streaks("date", "asc")
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_1["end"] == to_datetime("2023-05-30 08:17:54")
        assert streak_1["length"] == 2
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-06-17 17:18:19")
        assert streak_2["end"] == to_datetime("2023-06-20 11:15:43")
        assert streak_2["length"] == 4
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-06-25 19:54:07")
        assert streak_3["end"] == to_datetime("2023-06-27 19:00:28")
        assert streak_3["length"] == 3

        # sort by length, descending
        streaks = habit.get_all_streaks("length", "desc")
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-06-17 17:18:19")
        assert streak_1["end"] == to_datetime("2023-06-20 11:15:43")
        assert streak_1["length"] == 4
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-06-25 19:54:07")
        assert streak_2["end"] == to_datetime("2023-06-27 19:00:28")
        assert streak_2["length"] == 3
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_3["end"] == to_datetime("2023-05-30 08:17:54")
        assert streak_3["length"] == 2

        # sort by length, ascending
        streaks = habit.get_all_streaks("length", "asc")
        assert len(streaks) == 3
        streak_1 = streaks[0]
        assert streak_1["start"] == to_datetime("2023-05-29 11:23:45")
        assert streak_1["end"] == to_datetime("2023-05-30 08:17:54")
        assert streak_1["length"] == 2
        streak_2 = streaks[1]
        assert streak_2["start"] == to_datetime("2023-06-25 19:54:07")
        assert streak_2["end"] == to_datetime("2023-06-27 19:00:28")
        assert streak_2["length"] == 3
        streak_3 = streaks[2]
        assert streak_3["start"] == to_datetime("2023-06-17 17:18:19")
        assert streak_3["end"] == to_datetime("2023-06-20 11:15:43")
        assert streak_3["length"] == 4

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
