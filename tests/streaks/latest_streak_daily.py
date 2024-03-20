from modules import db
from modules.utils import to_datetime
from classes.habit import Habit


class TestLatestStreakForDailyHabit:
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
        habit = Habit("Practise piano", "daily", "2023-05-28 09:21:57")
        habit.perform("2023-05-31 11:17:49")
        habit.perform("2023-06-15 17:00:34")
        habit.perform("2023-06-17 00:55:21")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-06-17 00:55:21")
        assert current_streak["end"] == to_datetime("2023-06-17 00:55:21")
        assert current_streak["length"] == 1

    def test_one_period_streak_with_multiple_performances_per_period(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
        habit.perform("2023-05-31 00:55:21")
        habit.perform("2023-05-31 11:17:49")
        habit.perform("2023-05-31 17:00:34")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-05-31 00:55:21")
        assert current_streak["end"] == to_datetime("2023-05-31 17:00:34")
        assert current_streak["length"] == 1

    def test_multi_period_streak(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
        habit.perform("2023-05-31 00:55:21")
        habit.perform("2023-06-01 11:17:49")
        habit.perform("2023-06-02 17:00:34")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-05-31 00:55:21")
        assert current_streak["end"] == to_datetime("2023-06-02 17:00:34")
        assert current_streak["length"] == 3

    def test_multi_period_streak_with_multiple_performances_per_period(self):
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
        assert current_streak["start"] == to_datetime("2023-06-15 00:19:04")
        assert current_streak["end"] == to_datetime("2023-06-17 23:36:26")
        assert current_streak["length"] == 3

    def test_with_many_streaks(self):
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
        assert current_streak["start"] == to_datetime("2023-06-22 16:03:57")
        assert current_streak["end"] == to_datetime("2023-06-22 16:03:57")
        assert current_streak["length"] == 1

    def test_latest_streak_is_old(self):
        """
        If today can only start a fresh streak, the last streak that was achieved should be returned.
        """
        habit = Habit("Practise piano", "daily", "2023-05-28 19:03:25")
        habit.perform("2023-05-29 18:15:36")
        habit.perform("2023-05-30 20:03:45")
        habit.perform("2023-05-31 19:12:46")
        latest_streak = habit.get_latest_streak(to_datetime("2023-06-05 15:00:00"))
        assert latest_streak["start"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["end"] == to_datetime("2023-05-31 19:12:46")
        assert latest_streak["is_current"] is False
        assert latest_streak["can_extend_today"] is False

    def test_latest_streak_is_recent(self):
        """
        If today could extend a streak, the latest streak should be returned, along with an indication that the
        "window" to extend the streak is still open.
        """
        habit = Habit("Practise piano", "daily", "2023-05-28 19:03:25")
        habit.perform("2023-05-29 18:15:36")
        habit.perform("2023-05-30 20:03:45")
        habit.perform("2023-05-31 19:12:46")
        latest_streak = habit.get_latest_streak(to_datetime("2023-06-01 15:00:00"))
        assert latest_streak["start"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["end"] == to_datetime("2023-05-31 19:12:46")
        assert latest_streak["is_current"] is True
        assert latest_streak["can_extend_today"] is True

    def test_latest_streak_is_current(self):
        """
        If today is part of an ongoing streak, the details of the streak should be returned, as well as an indication
        that today falls within the period range of the streak.
        :return:
        """
        habit = Habit("Practise piano", "daily", "2023-05-28 19:03:25")
        habit.perform("2023-05-29 18:15:36")
        habit.perform("2023-05-30 20:03:45")
        habit.perform("2023-05-31 19:12:46")
        latest_streak = habit.get_latest_streak(to_datetime("2023-05-31 20:00:00"))
        assert latest_streak["start"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["end"] == to_datetime("2023-05-31 19:12:46")
        assert latest_streak["is_current"] is True
        assert latest_streak["can_extend_today"] is False

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
