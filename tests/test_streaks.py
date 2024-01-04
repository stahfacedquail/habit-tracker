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
        assert streak_1["start"] == utils.to_datetime("2023-05-28 18:15:55")
        assert streak_1["end"] == utils.to_datetime("2023-05-30 16:57:59")
        assert streak_1["length"] == 3
        streak_2 = streaks[1]
        assert streak_2["start"] == utils.to_datetime("2023-06-02 19:29:09")
        assert streak_2["end"] == utils.to_datetime("2023-06-08 18:53:14")
        assert streak_2["length"] == 7

    def test_streak_at_end_of_list(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:15:43")
        habit.perform("2023-06-17 16:48:06")
        habit.perform("2023-06-18 18:59:43")
        habit.perform("2023-06-22 20:22:13")

        streaks = habit.get_all_streaks()
        assert len(streaks) == 1
        streak = streaks[0]
        assert streak["start"] == utils.to_datetime("2023-06-17 16:48:06")
        assert streak["end"] == utils.to_datetime("2023-06-18 18:59:43")
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

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()

class TestStreaksForWeeklyHabits:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    # 1. test streak at the end of the list
    # 2. test streak when multiple performances per week
    # 3. test more than one streak in list
    # 4. test no streaks

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()