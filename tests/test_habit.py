from datetime import date
from modules import db, utils
from classes.habit import Habit


# TODO: Rethink time tests - use freezegun for consistency (timezones)
class TestHabit:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_create_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        assert habit.get_uuid() is not None
        assert habit.get_title() == "Practise piano"
        assert habit.get_recurrence() == "daily"
        assert habit.get_created_at() == utils.to_datetime("2023-05-28 18:57:19")
        assert len(habit.get_activities()) == 0

    def test_create_habit_with_db_timestamp(self):
        habit = Habit("Water plants", "weekly")
        today = date.today()
        assert habit.get_uuid() is not None
        assert habit.get_title() == "Water plants"
        assert habit.get_recurrence() == "weekly"
        assert habit.get_created_at() is not None
        assert habit.get_created_at().day == today.day
        assert habit.get_created_at().month == today.month
        assert habit.get_created_at().year == today.year
        assert len(habit.get_activities()) == 0

    def test_perform_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        habit.perform("2023-05-29 21:00:43")
        assert len(habit.get_activities()) == 1
        execution = habit.get_activities()[0]
        assert execution.get_uuid() is not None
        assert execution.get_habit_uuid() == habit.get_uuid()
        assert execution.get_performed_at() == utils.to_datetime("2023-05-29 21:00:43")

    # TODO: Need to test this with freezegun instead because timestamp difference in timezone
    def test_perform_habit_with_db_timestamp(self):
        habit = Habit("Practise piano", "daily")
        habit.perform()
        today = date.today()
        assert len(habit.get_activities()) == 1
        execution = habit.get_activities()[0]
        assert execution.get_uuid() is not None
        assert execution.get_habit_uuid() == habit.get_uuid()
        assert execution.get_performed_at().day == today.day
        assert execution.get_performed_at().month == today.month
        assert execution.get_performed_at().year == today.year

    def test_fetch_habit(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:01:33")
        habit.perform()
        habit_id = habit.get_uuid()

        habit_copy = Habit(habit_id)
        assert habit_copy.get_uuid() == habit_id
        assert habit_copy.get_title() == "Practise piano"
        assert habit_copy.get_recurrence() == "daily"
        assert habit_copy.get_created_at() == utils.to_datetime("2023-05-28 19:01:33")
        assert len(habit_copy.get_activities()) == 1

    def test_initialise_from_db_dict_item(self):
        db_item = {
            "habit": ("dbf01807-ef61-485f-9637-cd53ee49e09e", "Practise piano", "daily", "2023-05-28 19:33:12"),
            "activities": [
                ("c9b9b03e-90b4-40af-b38d-0f0dd94ed190", "dbf01807-ef61-485f-9637-cd53ee49e09e", "2023-05-29 19:23:00"),
                ("bc6e8b96-e019-48ef-aaaa-4102cb8fab32", "dbf01807-ef61-485f-9637-cd53ee49e09e", "2023-05-31 05:15:23")
            ]
        }
        habit_model = Habit(db_item)
        assert habit_model.get_uuid() == "dbf01807-ef61-485f-9637-cd53ee49e09e"
        assert habit_model.get_title() == "Practise piano"
        assert habit_model.get_recurrence() == "daily"
        assert habit_model.get_created_at() == utils.to_datetime("2023-05-28 19:33:12", True)  # "straight" from db
        assert len(habit_model.get_activities()) == 2

    def test_to_string(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        habit_string = str(habit).split("\n")
        assert habit_string[0] == "Title: Practise piano"
        assert habit_string[1] == "Recurs: daily"
        assert habit_string[2] == "Created at: 2023-05-28 18:57:19"
        assert habit_string[3] == "Has been performed 0 times"

        habit.perform()
        habit_string = str(habit).split("\n")
        assert habit_string[3] == "Has been performed 1 time"

        habit.perform()
        habit.perform()
        habit.perform()
        habit_string = str(habit).split("\n")
        assert habit_string[3] == "Has been performed 4 times"

    def test_get_last_performed_date(self):
        habit = Habit("Phone parents", "weekly", "2023-05-29 19:04:55")
        habit.perform("2023-05-29 21:12:32")
        habit.perform("2023-05-31 14:54:22")
        habit.perform("2023-06-11 06:55:10")
        habit.perform("2023-06-17 18:25:43")
        habit.perform("2023-06-25 20:46:06")

        # TODO: Compare dates like in other places
        last_performed_dt = habit.get_date_last_performed()
        assert last_performed_dt.year == 2023
        assert last_performed_dt.month == 6
        assert last_performed_dt.day == 25
        assert last_performed_dt.hour == 20
        assert last_performed_dt.minute == 46
        assert last_performed_dt.second == 6

    def test_get_last_performed_date_with_no_activities(self):
        habit = Habit("Phone parents", "weekly", "2023-05-29 19:04:55")
        last_performed_dt = habit.get_date_last_performed()
        assert last_performed_dt is None

    def test_delete(self):
        habit = Habit("Phone parents", "weekly", "2023-05-29 19:04:55")
        habit.perform("2023-05-29 21:12:32")
        habit.perform("2023-05-31 14:54:22")
        habit.perform("2023-06-11 06:55:10")
        habit.perform("2023-06-17 18:25:43")
        habit.perform("2023-06-25 20:46:06")

        uuid = habit.get_uuid()
        habit.remove()
        db_item = db.get_habit(uuid)
        assert db_item["habit"] is None
        assert db_item["activities"] == []

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
