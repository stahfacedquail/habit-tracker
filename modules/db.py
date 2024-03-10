import sqlite3
from typing import Optional

from modules import example_data
from modules.utils import make_uuid

# global database connection for the application
db_connection = None


def connect(db_name="main.db"):
    global db_connection
    db_connection = sqlite3.connect(db_name)


def disconnect():
    db_connection.close()


def setup_tables():
    """
    If the required tables aren't all present, clear out the database and create them afresh
    :return: Indication of whether the table setup had to be done or not
    """
    cur = db_connection.cursor()

    # check if tables exist
    cur.execute("SELECT name FROM sqlite_master WHERE name IN ('habits', 'activities', 'recurrence_types')")
    tables = cur.fetchall()
    if len(tables) == 3:  # all the expected tables are there; no need to re-create
        return False

    # just start afresh if some of the expected tables aren't there
    remove_tables()

    cur.execute("CREATE TABLE recurrence_types(type TEXT PRIMARY KEY)")

    cur.execute("""
        CREATE TABLE habits(
            uuid TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            recurrence TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recurrence)
                REFERENCES recurrence_types (type)
        )
    """)

    cur.execute("""
        CREATE TABLE activities(
            uuid TEXT PRIMARY KEY,
            habit TEXT NOT NULL,
            performed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit)
                REFERENCES habits(uuid)
        )
    """)

    return True


def remove_tables():
    cur = db_connection.cursor()
    cur.execute("DROP TABLE IF EXISTS recurrence_types")
    cur.execute("DROP TABLE IF EXISTS activities")
    cur.execute("DROP TABLE IF EXISTS habits")


def populate_starter_data():
    cur = db_connection.cursor()

    cur.execute("""
            INSERT INTO recurrence_types VALUES
                ("daily"),
                ("weekly")
        """)
    db_connection.commit()

    cur.executemany("""
            INSERT INTO habits VALUES (?, ?, ?, ?)
        """, example_data.habits)
    db_connection.commit()

    cur.executemany("""
            INSERT INTO activities VALUES(?, ?, ?)
        """, example_data.activities)
    db_connection.commit()


def create_habit(title, recurrence, created_at: Optional[str] = None):
    """
    Create a record in the database for this habit
    :param title: The title of the new habit
    :param recurrence: How frequently the habit should be performed
    :param created_at: A datetime string (in GMT) when the habit was created, with the format YYYY-mm-DD HH:MM:SS
    :return: The newly-created record, which is returned as a tuple
    """
    uuid = make_uuid()

    cur = db_connection.cursor()
    if created_at is None:
        cur.execute("""
            INSERT INTO habits(uuid, title, recurrence)
            VALUES(?, ?, ?)
        """, (uuid, title, recurrence))
    else:
        cur.execute("""
            INSERT INTO habits VALUES(?, ?, ?, ?)
        """, (uuid, title, recurrence, created_at))
    db_connection.commit()
    return get_habit(uuid)


def create_activity(habit_uuid, performed_at):
    """
        Create a record in the database for this performance of a given habit
        :param habit_uuid: The uuid of the habit that was performed
        :param performed_at: A datetime string (in GMT) when the habit was performed, with the format
            YYYY-mm-DD HH:MM:SS
        :return: The newly-created record, which is returned as a tuple
        """
    uuid = make_uuid()

    cur = db_connection.cursor()
    if performed_at is None:
        cur.execute("""
            INSERT INTO activities(uuid, habit) VALUES(?, ?)
        """, (uuid, habit_uuid))
    else:
        cur.execute("""
            INSERT INTO activities VALUES(?, ?, ?)
        """, (uuid, habit_uuid, performed_at))
    db_connection.commit()

    cur.execute("SELECT * FROM activities WHERE uuid = ?", (uuid, ))
    return cur.fetchone()


def get_habit(uuid):
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM habits WHERE uuid = ?", (uuid, ))
    habit = cur.fetchone()
    cur.execute("SELECT * FROM activities WHERE habit = ? ORDER BY performed_at ASC", (uuid, ))
    activities = cur.fetchall()
    return {
        "habit": habit,
        "activities": activities,
    }


def delete_habit(uuid):
    cur = db_connection.cursor()
    cur.execute("DELETE FROM activities WHERE habit = ?", (uuid,))
    db_connection.commit()
    cur.execute("DELETE FROM habits WHERE uuid = ?", (uuid,))
    db_connection.commit()


def get_all_habits():
    """
    Fetch all the habit records, as well as all the activity records.
    :return: A list of dictionary objects, where each object has a "habit" key whose value is a tuple containing the
        data of one record from the "habits" table, and an "activities" key whose value is a list of tuples, each of
        which contain the data of one record from the "activities" table.  The activities are the subset belonging to
        that particular habit.
    """
    cur = db_connection.cursor()
    cur.execute("SELECT * FROM habits ORDER BY uuid ASC")
    habit_tuples = cur.fetchall()
    augmented_habits = []  # i.e. habits with their list of when they got done

    cur.execute("SELECT * FROM activities ORDER BY habit ASC, performed_at ASC")
    activity_tuples = cur.fetchall()

    activity_idx = 0  # index to loop from start to end of `activity_tuples`
    for habit in habit_tuples:
        augmented_habit = {
            "habit": habit,
            "activities": []
        }
        habit_id = habit[0]

        # Since activities were fetched ordered by their parent habit's id, we will add one activity at a time to a
        # habit, until we encounter the first activity to have a different parent habit than the one we are currently
        # considering (i.e. `habit`).  At that point, we will know to move on to the next habit in `habit_tuples`.
        for idx in range(activity_idx, len(activity_tuples)):
            activity = activity_tuples[idx]
            parent_habit_id = activity[1]
            if parent_habit_id == habit_id:
                augmented_habit["activities"].append(activity)
            else:
                activity_idx = idx  # Make a note to continue looking at the activities from this index
                break

        augmented_habits.append(augmented_habit)

    return augmented_habits


def get_all_habits_abridged():
    cur = db_connection.cursor()
    cur.execute("SELECT uuid, title FROM habits")
    habits = cur.fetchall()
    return habits

