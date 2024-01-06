import datetime

from db import create_habit, get_habit
from multimethod import multimethod
from typing import Union, Optional
from functools import reduce
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
        recent.  Determine the date ranges for which activities were recorded for 2 or more consecutive periods
        (days/weeks).
        :return: A list of dictionary objects, where each object has the start date and end date of the streak,
            the length of the streak, and the unit of measurement for the length of the streak (i.e. "days" or "weeks")
        """
        # 1. Add a computed property to each activity, namely, a string with just the date (no time) when the activity
        # was performed (daily habits) or the date of the Monday of the week when it was performed (weekly habits)
        augmented_activities = list(map(
            lambda x: {
                "model": x,
                "performance_period": utils.to_date_only_string(
                    x.get_performed_at() if self.__recurrence__ == "daily"
                    else utils.get_week_start_date(x.get_performed_at())
                )
            }, self.__activities__))

        for a in augmented_activities:
            print(a["performance_period"])

        # 2. This is a function to group activities that were performed on the same day.  The result will be a
        # dictionary where each key is a date string like "2023-12-01" and the value is the list of Activity models for
        # that date (i.e. records of the habit being performed on that day/week, no matter the time)
        def group_by_date(grouped, activity):
            curr_date = activity["performance_period"]
            if curr_date not in grouped:
                grouped[curr_date] = []
            grouped[curr_date].append(activity["model"])
            return grouped

        dict_activities_per_day = reduce(group_by_date, augmented_activities, {})

        # 3. Extract a list of the unique dates on which the habit was performed and make sure it's sorted in ascending
        # order.
        active_dates = list(dict_activities_per_day.keys())
        active_dates.sort()

        # 4. Now for the business of computing the streaks.
        # `streaks`: Initially, this will just be a list of tuples like ("2023-12-01", "2023-12-04"), indicating when a
        # streak started and ended
        streaks = []
        # `streak_start`: If we peek ahead and see that we are observing a streak, this variable will hold onto the date
        # currently being looked at
        streak_start = None
        # `streak_length` keeps count of how many unique periods (days/weeks) make up the streak
        streak_length = 0
        # `interval` is the number of days that make up the recurrence period
        interval = 1 if self.__recurrence__ == "daily" else 7

        for (idx, dt_string) in enumerate(active_dates):
            curr_dt = utils.to_datetime(f"{dt_string} 00:00:00")

            if (idx + 1) < len(active_dates):  # there is another date after this one
                next_dt = utils.to_datetime(f"{active_dates[idx + 1]} 00:00:00")

                if streak_start is None:  # we are not busy observing a streak
                    streak_start = curr_dt  # so maybe this is the beginning of one; who knows!
                    streak_length = 1

                days_to_next_date = utils.get_num_days_from_to(streak_start, next_dt, False)
                if days_to_next_date == streak_length * interval:
                    # matches the expected days to get to the nth-following day/week, so increment streak length
                    streak_length += 1
                else:  # next date is beyond the nth-following day/week
                    if streak_length > 1:  # and we were busy observing a streak, so this terminates it
                        streaks.append((utils.to_date_only_string(streak_start), dt_string))

                    # reset to indicate we are ready to observe a new streak
                    streak_start = None
                    streak_length = 0
            else:  # no dates left to compare to
                # if we were busy observing a streak, this terminates it
                if streak_length > 1:
                    streaks.append((utils.to_date_only_string(streak_start), dt_string))

        def get_streak_accurate_params(start_date_activities: str, end_date_activities: str, habit_recurrence: str):
            def get_first_activity(activities: list[object]):
                activities.sort(key=lambda activity: activity.get_performed_at())
                return activities[0]

            def get_last_activity(activities: list[object]):
                activities.sort(key=lambda activity: activity.get_performed_at())
                return activities[-1]

            accurate_start = get_first_activity(start_date_activities).get_performed_at()
            accurate_end = get_last_activity(end_date_activities).get_performed_at()
            length = utils.get_num_days_from_to(accurate_start, accurate_end) if habit_recurrence == "daily" \
                else utils.get_num_weeks_from_to(accurate_start, accurate_end)
            return {
                "start": accurate_start,
                "end": accurate_end,
                "length": length,
                "unit": "days" if habit_recurrence == "daily" else "weeks"
            }

        return list(map(
            lambda streak: get_streak_accurate_params(
                dict_activities_per_day[streak[0]],
                dict_activities_per_day[streak[1]],
                self.__recurrence__
            ),
            streaks
        ))
