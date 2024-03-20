from modules import db
from modules.utils import to_datetime
from classes.habit import Habit


class TestLatestStreakForWeeklyHabit:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_no_activities(self):
        habit = Habit("Jog", "weekly", "2023-05-28 09:22:57")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] is None
        assert current_streak["end"] is None
        assert current_streak["length"] == 0
        assert current_streak["is_current"] is None
        assert current_streak["can_extend_today"] is None

    def test_one_period_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 09:21:57")
        habit.perform("2023-05-31 10:17:49")
        habit.perform("2023-06-15 18:00:34")
        habit.perform("2023-06-28 00:55:21")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-06-28 00:55:21")
        assert current_streak["end"] == to_datetime("2023-06-28 00:55:21")
        assert current_streak["length"] == 1

    def test_one_period_streak_with_multiple_performances_per_period(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
        habit.perform("2023-05-31 00:55:21")
        habit.perform("2023-06-03 11:17:49")
        habit.perform("2023-06-03 12:06:52")
        habit.perform("2023-06-04 17:00:34")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-05-31 00:55:21")
        assert current_streak["end"] == to_datetime("2023-06-04 17:00:34")
        assert current_streak["length"] == 1

    def test_multi_period_streak(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
        habit.perform("2023-05-31 00:55:21")
        habit.perform("2023-06-07 11:17:49")
        habit.perform("2023-06-12 17:00:34")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-05-31 00:55:21")
        assert current_streak["end"] == to_datetime("2023-06-12 17:00:34")
        assert current_streak["length"] == 3

    def test_multi_period_streak_with_multiple_performances_per_period(self):
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
        assert current_streak["start"] == to_datetime("2023-06-30 14:18:32")
        assert current_streak["end"] == to_datetime("2023-07-10 22:11:33")
        assert current_streak["length"] == 3

    def test_with_many_streaks(self):
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:21:57")
        habit.perform("2023-05-31 00:55:21")
        habit.perform("2023-06-07 11:17:49")
        habit.perform("2023-06-12 17:00:34")
        habit.perform("2023-06-30 00:55:21")
        habit.perform("2023-07-06 11:17:49")
        current_streak = habit.get_latest_streak()
        assert current_streak is not None
        assert current_streak["start"] == to_datetime("2023-06-30 00:55:21")
        assert current_streak["end"] == to_datetime("2023-07-06 11:17:49")
        assert current_streak["length"] == 2

    def test_latest_streak_is_old(self):
        """
        If today can only start a fresh streak, the last streak that was achieved should be returned.
        """
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:03:25")
        habit.perform("2023-05-29 18:15:36")
        latest_streak = habit.get_latest_streak(to_datetime("2023-06-12 15:00:00"))
        assert latest_streak["start"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["end"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["is_current"] is False
        assert latest_streak["can_extend_today"] is False

    def test_latest_streak_is_recent(self):
        """
        If today could extend a streak, the latest streak should be returned, along with an indication that the
        "window" to extend the streak is still open.
        """
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:03:25")
        habit.perform("2023-05-29 18:15:36")
        latest_streak = habit.get_latest_streak(to_datetime("2023-06-07 15:00:00"))
        assert latest_streak["start"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["end"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["is_current"] is True
        assert latest_streak["can_extend_today"] is True

    def test_latest_streak_is_current(self):
        """
        If today is part of an ongoing streak, the details of the streak should be returned, as well as an indication
        that today falls within the period range of the streak.
        """
        habit = Habit("Phone parents", "weekly", "2023-05-28 19:03:25")
        habit.perform("2023-05-29 18:15:36")
        latest_streak = habit.get_latest_streak(to_datetime("2023-06-01 15:00:00"))
        assert latest_streak["start"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["end"] == to_datetime("2023-05-29 18:15:36")
        assert latest_streak["is_current"] is True
        assert latest_streak["can_extend_today"] is False

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
