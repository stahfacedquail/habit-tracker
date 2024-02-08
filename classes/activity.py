from multimethod import multimethod
from typing import Optional
from modules.db import create_activity
from modules import utils


class Activity:
    @multimethod
    def __init__(self, habit_uuid: str, performed_at: Optional[str] = None):
        """
        Create a new activity in the database and then initialise a model to represent the newly-created activity.
        :param habit_uuid: The uuid of the habit that's being performed
        :param performed_at: The date/time at which the habit was performed, as specified by the user.  If not
            specified, the database will add a timestamp when the record is created.
        """
        new_activity = create_activity(habit_uuid, performed_at)
        self.__parse_from_db__(new_activity)

    @multimethod
    def __init__(self, activity_tuple: tuple[str, str, str]):
        """
        Given a record from the `activities` database table, transfer the data to this `Activity` model object
        :param activity_tuple: A record from the `activities` database table
        """
        self.__parse_from_db__(activity_tuple)

    def get_uuid(self):
        return self.__uuid__

    def get_habit_uuid(self):
        return self.__habit__

    def get_performed_at(self):
        return self.__performed_at__

    def __parse_from_db__(self, activity_tuple: tuple[str, str, str]):
        """
        Translate the data from an activity database record to this `Activity` model object.
        :param activity_tuple: A record from the `activities` database table
        :return: None
        """
        self.__uuid__ = activity_tuple[0]
        self.__habit__ = activity_tuple[1]
        self.__performed_at__ = utils.to_datetime(activity_tuple[2])

    def __str__(self):
        return f"Habit {self.__habit__} performed at {self.__performed_at__}"
