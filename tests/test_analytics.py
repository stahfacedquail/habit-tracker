from datetime import datetime
from modules import db, utils, analytics
from classes.habit import Habit


class TestAnalytics:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()
        self.prepare_data()

    def prepare_data(self):
        habit_1 = Habit("Practise piano", "daily", "2023-05-28 19:21:57")
        habit_1.perform("2023-05-31 00:55:21")
        habit_1.perform("2023-06-01 11:17:49")
        habit_1.perform("2023-06-12 17:00:34")
        habit_1.perform("2023-06-15 00:55:21")
        habit_1.perform("2023-06-16 11:17:49")
        habit_1.perform("2023-06-17 15:23:44")
        habit_1.perform("2023-06-21 16:03:57")

        habit_2 = Habit("phone parents", "weekly", "2023-06-14 19:01:16")
        habit_2.perform("2023-06-18 16:20:30")
        habit_2.perform("2023-06-21 16:42:11")
        habit_2.perform("2023-06-21 21:30:31")
        habit_2.perform("2023-06-23 20:30:47")
        habit_2.perform("2023-06-24 06:16:00")
        habit_2.perform("2023-06-24 13:00:01")
        habit_2.perform("2023-06-24 20:57:17")

        habit_3 = Habit("Water plants", "weekly", "2023-06-19 15:43:21")

    def test_get_all_habits_with_stats(self):
        expected_values_1 = {
            "title": "Practise piano",
            "created_at": utils.to_datetime("2023-05-28 19:21:57"),
            "recurrence": "daily",
            "last_performed": utils.to_datetime("2023-06-21 16:03:57"),
            "num_periods_performed": 7,
            "completion_rate": 24,  # as percentage,
            "latest_streak": 1,
        }

        expected_values_2 = {
            "title": "phone parents",
            "created_at": utils.to_datetime("2023-06-14 19:01:16"),
            "recurrence": "weekly",
            "last_performed": utils.to_datetime("2023-06-24 20:57:17"),
            "num_periods_performed": 2,
            "completion_rate": 100,  # as percentage,
            "latest_streak": 2,
        }

        expected_values_3 = {
            "title": "Water plants",
            "created_at": utils.to_datetime("2023-06-19 15:43:21"),
            "recurrence": "weekly",
            "last_performed": None,
            "num_periods_performed": 0,
            "completion_rate": 0,
            "latest_streak": 0,
        }

        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        # Sort into an order that will be the same regardless of text execution (from db, they are sorted by uuid, so
        # `habit_1`, `habit_2` and `habit_3` will appear in different orders depending on the uuids that get generated
        # per execution of the test.  We therefore sort by `created_at` as that is a value we control on creation of
        # each habit here.
        habits.sort(key=lambda h: h["created_at"])

        assert len(habits) == 3

        assert habits[0]["title"] == expected_values_1["title"]
        assert habits[0]["created_at"] == expected_values_1["created_at"]
        assert habits[0]["recurrence"] == expected_values_1["recurrence"]
        assert habits[0]["last_performed"] == expected_values_1["last_performed"]
        assert habits[0]["num_periods_performed"] == expected_values_1["num_periods_performed"]
        assert habits[0]["latest_streak"] == expected_values_1["latest_streak"]
        assert habits[0]["completion_rate"] == expected_values_1["completion_rate"]

        assert habits[1]["title"] == expected_values_2["title"]
        assert habits[1]["created_at"] == expected_values_2["created_at"]
        assert habits[1]["recurrence"] == expected_values_2["recurrence"]
        assert habits[1]["last_performed"] == expected_values_2["last_performed"]
        assert habits[1]["num_periods_performed"] == expected_values_2["num_periods_performed"]
        assert habits[1]["latest_streak"] == expected_values_2["latest_streak"]
        assert habits[1]["completion_rate"] == expected_values_2["completion_rate"]

        assert habits[2]["title"] == expected_values_3["title"]
        assert habits[2]["created_at"] == expected_values_3["created_at"]
        assert habits[2]["recurrence"] == expected_values_3["recurrence"]
        assert habits[2]["last_performed"] == expected_values_3["last_performed"]
        assert habits[2]["num_periods_performed"] == expected_values_3["num_periods_performed"]
        assert habits[2]["latest_streak"] == expected_values_3["latest_streak"]
        assert habits[2]["completion_rate"] == expected_values_3["completion_rate"]

    def test_sort_ascending_order(self):
        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        sorted_habits = analytics.sort_habits(habits, "num_periods_performed", "asc")
        assert sorted_habits[0]["title"] == "Water plants"
        assert sorted_habits[1]["title"] == "phone parents"
        assert sorted_habits[2]["title"] == "Practise piano"

    def test_sort_descending_order(self):
        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        sorted_habits = analytics.sort_habits(habits, "completion_rate", "desc")
        assert sorted_habits[0]["title"] == "phone parents"
        assert sorted_habits[1]["title"] == "Practise piano"
        assert sorted_habits[2]["title"] == "Water plants"

    def test_sort_with_none_type_values(self):
        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        sorted_habits = analytics.sort_habits(habits, "last_performed", "asc")
        assert sorted_habits[0]["title"] == "Water plants"
        assert sorted_habits[1]["title"] == "Practise piano"
        assert sorted_habits[2]["title"] == "phone parents"

    def test_sort_is_case_insensitive(self):
        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        sorted_habits = analytics.sort_habits(habits, "title", "asc")
        assert sorted_habits[0]["title"] == "phone parents"
        assert sorted_habits[1]["title"] == "Practise piano"
        assert sorted_habits[2]["title"] == "Water plants"

    def test_filter_returns_results(self):
        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        filtered_habits = analytics.filter_habits(habits, "recurrence", "weekly")
        assert len(filtered_habits) == 2

        filtered_habit_titles = list(map(lambda h: h["title"], filtered_habits))
        assert "Water plants" in filtered_habit_titles
        assert "phone parents" in filtered_habit_titles

    def test_filter_returns_no_results(self):
        habits = analytics.get_habits(datetime(2023, 6, 25, 16, 0, 0))
        filtered_habits = analytics.filter_habits(habits, "recurrence", "non_existent_type")
        assert len(filtered_habits) == 0

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
