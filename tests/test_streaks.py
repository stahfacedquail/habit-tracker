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
        assert streak_1["unit"] == "days"
        streak_2 = streaks[1]
        assert streak_2["start"] == utils.to_datetime("2023-06-02 19:29:09")
        assert streak_2["end"] == utils.to_datetime("2023-06-08 18:53:14")
        assert streak_2["length"] == 7
        assert streak_2["unit"] == "days"

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
        assert streak_1["unit"] == "weeks"

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
        assert streak_1["start"] == utils.to_datetime("2023-09-18 16:20:30")
        assert streak_1["end"] == utils.to_datetime("2023-09-28 21:30:31")
        assert streak_1["length"] == 2
        assert streak_2["start"] == utils.to_datetime("2024-01-06 17:39:39")
        assert streak_2["end"] == utils.to_datetime("2024-01-20 21:42:03")
        assert streak_2["length"] == 3

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

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()