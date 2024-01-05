import datetime

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

    def get_all_streaks(self):
        """
        By default, a habit's activities are ordered by the date on which they were performed, from oldest to most
        recent.  This function returns all the streaks achieved in the history of this habit, that is, all the times
        when the user managed to complete the habit
        (i) at least once per required time period and
        (ii) for more than 1 time period in a row.
        e.g. performing a daily habit for 3 consecutive days a streak, and so is performing a weekly habit for 5
        consecutive weeks.
        :return: A list of dictionary objects which each contain the start and end dates of a streak, as well as its
            length.
        """
        is_daily = self.__recurrence__ == "daily"

        group_activities_by_intervals = utils.group_performances_per_day if is_daily else utils.group_performances_per_week
        count_intervals_between = utils.get_num_days_from_to if is_daily else utils.get_num_weeks_from_to
        is_next_interval = utils.is_next_day if is_daily else utils.is_next_week

        activities_grouped_per_interval = group_activities_by_intervals(self)
        streaks = []

        # If we peek ahead and see that we are observing a streak, this variable holds onto the current activity group
        # (which contains the dates for the start of the streak)
        streak_start = None

        for (idx, activity_group) in enumerate(activities_grouped_per_interval):
            zeroed_interval_start = activity_group["interval_start"]  # the interval starts at midnight
            last_performance_in_interval = max(activity_group["activities"], key=lambda x: x.get_performed_at())

            # last activity group on the list; no further dates to compare to
            if (idx + 1) == len(activities_grouped_per_interval):
                # If we were busy observing a streak, this date must be the end of that streak
                if streak_start is not None:
                    actual_start = min(streak_start["activities"], key=lambda x: x.get_performed_at()).get_performed_at()
                    zeroed_start = streak_start["interval_start"]
                    actual_end = last_performance_in_interval.get_performed_at()
                    zeroed_end = activity_group["interval_start"]
                    streaks.append({
                        "start": actual_start,
                        "end": actual_end,
                        "length": count_intervals_between(zeroed_start, zeroed_end)
                    })
            else:  # we aren't at the end of the list yet
                next_activity_group = activities_grouped_per_interval[idx + 1]
                next_active_interval_start_date = next_activity_group["interval_start"]
                # If the next group of activities occurred directly after the current group and we are not currently
                # observing a streak already, then note that this current activity group is the beginning of a streak.
                if is_next_interval(zeroed_interval_start, next_active_interval_start_date):
                    if streak_start is None:
                        streak_start = activity_group
                else:
                    # This group of activities and the next group are not on consecutive intervals, so if we there was
                    # a streak that was running, it ends with the current group of activities.
                    if streak_start is not None:
                        actual_start = min(streak_start["activities"], key=lambda x: x.get_performed_at()).get_performed_at()
                        zeroed_start = streak_start["interval_start"]
                        actual_end = last_performance_in_interval.get_performed_at()
                        zeroed_end = activity_group["interval_start"]
                        streaks.append({
                            "start": actual_start,
                            "end": actual_end,
                            "length": count_intervals_between(zeroed_start, zeroed_end)
                        })
                        streak_start = None  # reset this variable to indicate that we are ready to observe a new streak

        return streaks
