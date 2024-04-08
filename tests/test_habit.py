from datetime import timedelta, datetime
from freezegun import freeze_time
from modules import db
from modules.utils import to_datetime
from classes.habit import Habit


class TestHabit:
    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()

    def test_create_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        assert habit.get_uuid() is not None
        assert habit.get_title() == "Practise piano"
        assert habit.get_recurrence() == "daily"
        assert habit.get_created_at() == to_datetime("2023-05-28 18:57:19")
        assert len(habit.get_activities()) == 0

    def test_create_habit_with_db_timestamp(self):
        now = datetime.now().replace(microsecond=0)  # db time resolution only goes to seconds
        habit = Habit("Water plants", "weekly")
        assert habit.get_uuid() is not None
        assert habit.get_title() == "Water plants"
        assert habit.get_recurrence() == "weekly"
        assert habit.get_created_at() is not None
        latest = now + timedelta(minutes=2)  # assuming habit creation wouldn't take longer than 2 minutes
        assert now <= habit.get_created_at() <= latest
        assert len(habit.get_activities()) == 0

    def test_perform_habit_with_manual_timestamp(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
        habit.perform("2023-05-29 21:00:43")
        assert len(habit.get_activities()) == 1
        execution = habit.get_activities()[0]
        assert execution.get_uuid() is not None
        assert execution.get_habit_uuid() == habit.get_uuid()
        assert execution.get_performed_at() == to_datetime("2023-05-29 21:00:43")

    def test_perform_habit_with_db_timestamp(self):
        habit = Habit("Practise piano", "daily")
        now = datetime.now().replace(microsecond=0)
        habit.perform()
        assert len(habit.get_activities()) == 1
        execution = habit.get_activities()[0]
        assert execution.get_uuid() is not None
        assert execution.get_habit_uuid() == habit.get_uuid()
        latest = now + timedelta(minutes=2)
        assert now <= execution.get_performed_at() <= latest

    def test_fetch_habit(self):
        habit = Habit("Practise piano", "daily", "2023-05-28 19:01:33")
        habit.perform()
        habit_id = habit.get_uuid()

        habit_copy = Habit(habit_id)
        assert habit_copy.get_uuid() == habit_id
        assert habit_copy.get_title() == "Practise piano"
        assert habit_copy.get_recurrence() == "daily"
        assert habit_copy.get_created_at() == to_datetime("2023-05-28 19:01:33")
        assert len(habit_copy.get_activities()) == 1

    @freeze_time(tz_offset=+6)
    def test_initialise_from_db_dict_item(self):
        db_item = {
            "habit": ("01234567-89ab-cdef-0123-456789abcdef", "Practise piano", "daily", "2023-05-28 19:33:12"),
            "activities": [
                ("12345678-9abc-def0-1234-56789abcdef0", "01234567-89ab-cdef-0123-456789abcdef", "2023-05-29 19:23:00"),
                ("23456789-abcd-ef01-2345-6789abcdef01", "01234567-89ab-cdef-0123-456789abcdef", "2023-05-31 05:15:23")
            ]
        }
        habit_model = Habit(db_item)
        assert habit_model.get_uuid() == "01234567-89ab-cdef-0123-456789abcdef"
        assert habit_model.get_title() == "Practise piano"
        assert habit_model.get_recurrence() == "daily"
        assert habit_model.get_created_at() == to_datetime("2023-05-29 01:33:12")
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

        last_performed_dt = habit.get_date_last_performed()
        assert last_performed_dt == to_datetime("2023-06-25 20:46:06")

    def test_get_last_performed_date_with_multiple_performances_in_last_period(self):
        habit = Habit("Jog", "daily", "2023-05-29 19:04:55")
        habit.perform("2023-05-29 21:12:32")
        habit.perform("2023-05-31 14:54:22")
        habit.perform("2023-06-01 06:55:10")
        habit.perform("2023-06-01 18:25:43")
        habit.perform("2023-06-01 22:46:06")

        last_performed_dt = habit.get_date_last_performed()
        assert last_performed_dt == to_datetime("2023-06-01 22:46:06")

    def test_get_last_performed_date_with_no_activities(self):
        habit = Habit("Phone parents", "weekly", "2023-05-29 19:04:55")
        last_performed_dt = habit.get_date_last_performed()
        assert last_performed_dt is None

    def test_get_singular_interval_label(self):
        habit_daily = Habit("Jog", "daily")
        assert habit_daily.get_interval_label(1) == "day"

        habit_weekly = Habit("Phone parents", "weekly")
        assert habit_weekly.get_interval_label(1) == "week"

    def test_get_plural_interval_label(self):
        habit_daily = Habit("Jog", "daily")
        assert habit_daily.get_interval_label(0) == "days"

        habit_weekly = Habit("Phone parents", "weekly")
        assert habit_weekly.get_interval_label(5) == "weeks"

    def test_delete_habit_without_activities(self):
        habit = Habit("Jog", "daily")
        uuid = habit.get_uuid()
        habit.remove()
        db_item = db.get_habit(uuid)
        assert db_item["habit"] is None
        assert db_item["activities"] == []

    def test_delete_habit_with_activities(self):
        habit = Habit("Phone parents", "weekly")
        for i in range(5):
            habit.perform()

        uuid = habit.get_uuid()
        habit.remove()
        db_item = db.get_habit(uuid)
        assert db_item["habit"] is None
        assert db_item["activities"] == []

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()
