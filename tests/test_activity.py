from datetime import datetime, timedelta
from freezegun import freeze_time
from modules import db
from classes.habit import Habit
from classes.activity import Activity
from modules.utils import to_datetime

class TestActivity:

    habit_uuid = None

    def setup_method(self):
        db.connect("test.db")
        db.setup_tables()
        habit = Habit("Jog", "daily", "2024-02-23 15:12:33")
        self.habit_uuid = habit.get_uuid()

    def test_initialise_with_explicit_timestamp(self):
        activity = Activity(self.habit_uuid, "2024-02-24 05:25:49")
        assert activity.get_uuid() is not None
        assert activity.get_habit_uuid() == self.habit_uuid
        assert activity.get_performed_at() == to_datetime("2024-02-24 05:25:49")

    def test_initialise_without_explicit_timestamp(self):
        now = datetime.now().replace(microsecond=0)  # db does not keep timestamps to microsecond resolution
        activity = Activity(self.habit_uuid)
        assert activity.get_uuid() is not None
        assert activity.get_habit_uuid() == self.habit_uuid
        latest = now + timedelta(minutes=2)  # surely the activity's timestamp won't be more than 2 minutes from now?
        assert now <= activity.get_performed_at() <= latest

    @freeze_time(tz_offset=-10)
    def test_initialise_from_db_tuple(self):
        """
        Note that times in the database are GMT, while the app uses the local timezone.
        """
        activity = Activity((
            "01234567-89ab-cdef-0123-456789abcdef",
            "abcdef01-2345-6789-abcd-ef0123456789",
            "2024-01-15 18:00:52"
        ))
        assert activity.get_uuid() == "01234567-89ab-cdef-0123-456789abcdef"
        assert activity.get_habit_uuid() == "abcdef01-2345-6789-abcd-ef0123456789"
        assert activity.get_performed_at() == to_datetime("2024-01-15 08:00:52")

    @freeze_time(tz_offset=+5)
    def test_to_string(self):
        activity = Activity((
            "12345678-9abc-def0-1234-56789abcdef0",
            "bcdef012-3456-789a-bcde-f0123456789a",
            "2024-01-15 21:00:52"
        ))
        assert str(activity) == "Habit bcdef012-3456-789a-bcde-f0123456789a performed at 2024-01-16 02:00:52"

    def teardown_method(self):
        db.remove_tables()
        db.disconnect()