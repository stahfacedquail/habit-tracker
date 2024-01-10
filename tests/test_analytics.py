from datetime import datetime
import analytics
import db
import utils
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

        habit_2 = Habit("Phone parents", "weekly", "2023-06-14 19:01:16")
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
            "completion_rate": {
                "num_active_periods": 7,
                "num_total_periods": 29,
                "rate": 24  # as percentage
            },
            "latest_streak": {
                "start": utils.to_datetime("2023-06-21 16:03:57"),
                "end": utils.to_datetime("2023-06-21 16:03:57"),
                "length": 1,
                "unit": "days",
                "is_current": False,
                "continuable_until": None,
            },
        }

        expected_values_2 = {
            "title": "Phone parents",
            "created_at": utils.to_datetime("2023-06-14 19:01:16"),
            "recurrence": "weekly",
            "last_performed": utils.to_datetime("2023-06-24 20:57:17"),
            "num_periods_performed": 2,
            "completion_rate": {
                "num_active_periods": 2,
                "num_total_periods": 2,
                "rate": 100  # as percentage
            },
            "latest_streak": {
                "start": utils.to_datetime("2023-06-18 16:20:30"),
                "end": utils.to_datetime("2023-06-24 20:57:17"),
                "length": 2,
                "unit": "weeks",
                "is_current": True,
                "continuable_until": None,
            },
        }

        expected_values_3 = {
            "title": "Water plants",
            "created_at": utils.to_datetime("2023-06-19 15:43:21"),
            "recurrence": "weekly",
            "last_performed": None,
            "num_periods_performed": 0,
            "completion_rate": {
                "num_active_periods": 0,
                "num_total_periods": 1,
                "rate": 0
            },
            "latest_streak": {
                "start": None,
                "end": None,
                "length": 0,
                "unit": "weeks",
                "is_current": None,
                "continuable_until": None,
            },
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

        completion_rate = habits[0]["completion_rate"]
        assert completion_rate["num_active_periods"] == expected_values_1["completion_rate"]["num_active_periods"]
        assert completion_rate["num_total_periods"] == expected_values_1["completion_rate"]["num_total_periods"]
        returned_perc = round(100 * completion_rate["rate"])
        assert returned_perc == expected_values_1["completion_rate"]["rate"]

        latest_streak = habits[0]["latest_streak"]
        assert latest_streak["start"] == expected_values_1["latest_streak"]["start"]
        assert latest_streak["end"] == expected_values_1["latest_streak"]["end"]
        assert latest_streak["length"] == expected_values_1["latest_streak"]["length"]
        assert latest_streak["unit"] == expected_values_1["latest_streak"]["unit"]
        assert latest_streak["is_current"] == expected_values_1["latest_streak"]["is_current"]
        assert latest_streak["continuable_until"] == expected_values_1["latest_streak"]["continuable_until"]

        assert habits[1]["title"] == expected_values_2["title"]
        assert habits[1]["created_at"] == expected_values_2["created_at"]
        assert habits[1]["recurrence"] == expected_values_2["recurrence"]
        assert habits[1]["last_performed"] == expected_values_2["last_performed"]
        assert habits[1]["num_periods_performed"] == expected_values_2["num_periods_performed"]

        completion_rate = habits[1]["completion_rate"]
        assert completion_rate["num_active_periods"] == expected_values_2["completion_rate"]["num_active_periods"]
        assert completion_rate["num_total_periods"] == expected_values_2["completion_rate"]["num_total_periods"]
        returned_perc = round(100 * completion_rate["rate"])
        assert returned_perc == expected_values_2["completion_rate"]["rate"]

        latest_streak = habits[1]["latest_streak"]
        assert latest_streak["start"] == expected_values_2["latest_streak"]["start"]
        assert latest_streak["end"] == expected_values_2["latest_streak"]["end"]
        assert latest_streak["length"] == expected_values_2["latest_streak"]["length"]
        assert latest_streak["unit"] == expected_values_2["latest_streak"]["unit"]
        assert latest_streak["is_current"] == expected_values_2["latest_streak"]["is_current"]
        assert latest_streak["continuable_until"] == expected_values_2["latest_streak"]["continuable_until"]

        assert habits[2]["title"] == expected_values_3["title"]
        assert habits[2]["created_at"] == expected_values_3["created_at"]
        assert habits[2]["recurrence"] == expected_values_3["recurrence"]
        assert habits[2]["last_performed"] == expected_values_3["last_performed"]
        assert habits[2]["num_periods_performed"] == expected_values_3["num_periods_performed"]

        completion_rate = habits[2]["completion_rate"]
        assert completion_rate["num_active_periods"] == expected_values_3["completion_rate"]["num_active_periods"]
        assert completion_rate["num_total_periods"] == expected_values_3["completion_rate"]["num_total_periods"]
        returned_perc = round(100 * completion_rate["rate"])
        assert returned_perc == expected_values_3["completion_rate"]["rate"]

        latest_streak = habits[2]["latest_streak"]
        assert latest_streak["start"] == expected_values_3["latest_streak"]["start"]
        assert latest_streak["end"] == expected_values_3["latest_streak"]["end"]
        assert latest_streak["length"] == expected_values_3["latest_streak"]["length"]
        assert latest_streak["unit"] == expected_values_3["latest_streak"]["unit"]
        assert latest_streak["is_current"] == expected_values_3["latest_streak"]["is_current"]
        assert latest_streak["continuable_until"] == expected_values_3["latest_streak"]["continuable_until"]

    def test_sort_on_primary_prop_ascending_order(self):
        pass
        habits = analytics.get_habits()
        sorted_habits = analytics.sort_habits(habits, "asc", "num_periods_performed")
        assert sorted_habits[0]["title"] == "Water plants"
        assert sorted_habits[1]["title"] == "Phone parents"
        assert sorted_habits[2]["title"] == "Practise piano"

    def test_sort_on_secondary_prop_descending_order(self):
        habits = analytics.get_habits()
        sorted_habits = analytics.sort_habits(habits, "desc", "completion_rate", "rate")
        assert sorted_habits[0]["title"] == "Phone parents"
        assert sorted_habits[1]["title"] == "Practise piano"
        assert sorted_habits[2]["title"] == "Water plants"

    def test_sort_with_none_type_values(self):
        habits = analytics.get_habits()
        sorted_habits = analytics.sort_habits(habits, "asc", "last_performed")
        assert sorted_habits[0]["title"] == "Water plants"
        assert sorted_habits[1]["title"] == "Practise piano"
        assert sorted_habits[2]["title"] == "Phone parents"

    def test_filter_returns_results(self):
        pass

    def test_filter_returns_no_results(self):
        pass

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
