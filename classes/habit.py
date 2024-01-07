from datetime import datetime
from multimethod import multimethod
from typing import Union, Optional
from db import create_habit, get_habit
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

    def get_streak_unit(self):
        return "days" if self.__recurrence__ == "daily" else "weeks"

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
        Determine the date ranges for which activities were recorded for 2 or more consecutive periods (days/weeks).
        :return: A list of dictionary objects, where each object has the start date and end date of the streak,
            the length of the streak, and the unit of measurement for the length of the streak (i.e. "days" or "weeks")
        """
        # 1. Group the activities by period (day/week performed)
        dict_activities_per_period = utils.group_activities_by_performance_period(
            self.__activities__, self.__recurrence__)

        # 2. Extract a list of the unique dates on which the habit was performed and make sure it's sorted in ascending
        # order.
        active_dates = sorted(dict_activities_per_period)

        # 3. Now for the business of computing the streaks.
        # `streaks`: Initially, this will just be a list of tuples like ("2023-12-01", "2023-12-04"), indicating when a
        # streak started and ended
        streaks = []
        # `streak_start`: Holds onto a date and uses it as the reference point as we iterate through the subsequent
        # dates to see if a streak is formed.  Once a streak breaks, `streak_start` will be replaced by the date that
        # broke the streak and the cycle of comparisons will resume.  `streak_start` being None indicates that we are
        # ready to start observing a new streak.
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

        return list(map(
            lambda streak: utils.get_streak_accurate_params(
                dict_activities_per_period[streak[0]],
                dict_activities_per_period[streak[1]],
                self
            ),
            streaks
        ))

    def get_current_streak(self):
        """
        Calculates the user's most recent streak, or if their most recent performance of the habit isn't part of a
        streak, that performance is returned as a "streak" that lasted for one period.
        :return: A dictionary object containing the accurate start and end dates of the streak, the length of the
            streak, and the unit of measurement for the streak based on the habit's recurrence type (i.e. either "days"
            or "weeks").
        """

        if len(self.__activities__) == 0:
            return {
                "length": 0,
                "start": None,
                "end": None,
                "unit": self.get_streak_unit()
            }

        activities_grouped_by_date = utils.group_activities_by_performance_period(self.__activities__,
                                                                                  self.__recurrence__)
        active_dates = sorted(activities_grouped_by_date, reverse=True) # sort from most recent performance to oldest

        if len(active_dates) > 1:
            streak_end = active_dates[0]  # most recent performance date
            streak_end_dt = utils.to_datetime(f"{streak_end} 00:00:00")
            streak_start = None  # need to figure out when this streak started
            streak_length = 1  # we definitely know it is at least 1 period long
            interval = 1 if self.__recurrence__ == "daily" else 7  # number of days that make up one period
            idx = 1  # start looking for the start of the streak from second date onwards
            while idx < len(self.__activities__) and streak_start is None:
                curr_dt = utils.to_datetime(f"{active_dates[idx]} 00:00:00")
                # `diff` is the difference in days between the current date and the end of the streak
                diff = utils.get_num_days_from_to(curr_dt, streak_end_dt, False)
                # If `curr_dt` is the date we are expecting in order for the streak to continue...
                if diff == interval * streak_length:
                    streak_length += 1  # ... document that the streak indeed goes on
                    if (idx + 1) == len(active_dates):
                        # If we've reached the end of the list, then `curr_dt` is the start of the streak
                        streak_start = active_dates[idx]
                    else:
                        # Otherwise, look at the next date to see if the streak includes it too
                        idx += 1
                else:
                    # `curr_dt` has broken the streak, so the actual start of the start is the date that came before it
                    streak_start = active_dates[idx - 1]
        else:  # only activities recorded happened in one period, so this is the beginning and the end of the streak
            streak_start = active_dates[0]
            streak_end = active_dates[0]

        return utils.get_streak_accurate_params(
            activities_grouped_by_date[streak_start],
            activities_grouped_by_date[streak_end],
            self
        )

    def get_number_of_times_completed(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """
        Counts the number of unique periods in which the habit has been performed.  Note that performing the habit five
        times in one period counts as it being completed once, not five times.  Either or both `start_date` and
        `end_date` can be omitted, e.g. omitting `end_date` will start counting from `start_date` until the most recent
        performance of the habit, and omitting both will calculate it from the first performance of the habit to the
        last one.
        :return: The number of unique periods within the date range as described above, on which the habit was performed
        """
        active_dates = list(utils.group_activities_by_performance_period())
