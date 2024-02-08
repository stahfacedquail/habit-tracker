from modules import db
from classes.habit import Habit


class TestDBQueries:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_get_all_habits(self):
        habit_1 = Habit("Practise piano", "2023-05-28 12:03:45")
        habit_1.perform("2023-05-29 15:16:34")
        habit_1.perform("2023-05-31 21:54:47")

        habit_2 = Habit("Phone parents", "2023-02-21 21:32:53")

        habit_models = sorted([habit_1, habit_2], key=lambda h: h.get_uuid())

        all_habits = db.get_all_habits()
        assert len(all_habits) == 2

        for idx, habit_model in enumerate(habit_models):
            db_habit = all_habits[idx]["habit"]
            assert db_habit[0] == habit_models[idx].get_uuid()
            db_activities = all_habits[idx]["activities"]
            if habit_model.get_title() == "Practise piano":
                assert len(db_activities) == 2
            else:
                assert len(db_activities) == 0


    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
