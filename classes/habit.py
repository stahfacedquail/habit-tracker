from db import create_habit, get_habit
from multimethod import multimethod
from typing import Union, Optional
import utils
from classes.activity import Activity


class Habit:

    @multimethod
    def __init__(self, title: str, recurrence: str, created_at: Optional[str] = None):
        """
        Create a new habit in the database and then initialise a model to represent the newly-created habit.
        :param title: The title of the habit
        :param recurrence: How often the habit should be performed, e.g. daily
        :param created_at: The date/time at which the habit was created, according to the user.  If not specified, the
            database will add a timestamp when the record is created.
        :return: None
        """
        created_habit = create_habit(title, recurrence, created_at)
        self.__parse_from_db__(created_habit)

    @multimethod
    def __init__(self, uuid: str):
        """
        Initialise the model to represent an existing habit (from the database).
        :param uuid: The uuid of the habit to fetch and create a model of.
        :return: None
        """
        fetched_habit = get_habit(uuid)
        self.__parse_from_db__(fetched_habit)

    def get_uuid(self):
        return self.__uuid__

    def get_title(self):
        return self.__title__

    def get_recurrence(self):
        return self.__recurrence__

    def get_created_at(self):
        return self.__created_at__

    def get_activities(self):
        return self.__activities__

    def __str__(self):
        return f"""Title: {self.__title__}
Recurs: {self.__recurrence__}
Created at: {self.__created_at__}
Has been performed {len(self.__activities__)} time{"" if len(self.__activities__) == 1 else "s"}"""

    def __refresh__(self):
        """
        Fetch a fresh version of the habit from the database.  Invoke this whenever data outside the `habits` table is
        changed because the model will need to be updated too.
        :return: None
        """
        fetched_habit = get_habit(self.__uuid__)
        self.__parse_from_db__(fetched_habit)

    def perform(self, performed_at: Optional[str] = None):
        """
        Indicate that this habit has been performed.
        :param performed_at: The date/time at which the habit was performed.  If not specified, the database
            will add the timestamp at which the record was created.
        :return: None
        """
        Activity(self.__uuid__, performed_at)
        self.__refresh__()

    def __parse_from_db__(self, db_item: dict[str, Union[tuple[str, ...], list[tuple[str, ...]]]]):
        """
        Transfer the data about a habit and its activities from the database to this `Habit` model object.
        :param db_item: A dictionary object like this: {
                habit: (..., ... ),
                activities: [
                    (..., ... ),
                    (..., ... ), etc
                ]
            }
        :return: None
        """
        db_habit = db_item["habit"]
        db_activities = db_item["activities"]

        self.__uuid__ = db_habit[0]
        self.__title__ = db_habit[1]
        self.__recurrence__ = db_habit[2]
        self.__created_at__ = utils.to_datetime(db_habit[3])

        self.__activities__ = []
        for activity in db_activities:
            self.__activities__.append(Activity(activity))
