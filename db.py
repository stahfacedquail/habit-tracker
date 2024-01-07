import sqlite3
import data
from utils import make_uuid

# global database connection for the application
# TODO: Instead of a global connection, return from `connect` and pass it around?
db_connection = None


def connect(db_name="main.db"):
    global db_connection
    db_connection = sqlite3.connect(db_name)


def disconnect():
    db_connection.close()


def setup_tables():
    cur = db_connection.cursor()
    # clear old data
    remove_tables()

    # create afresh
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
        """, data.predefined_habits)
    db_connection.commit()

    cur.executemany("""
            INSERT INTO activities VALUES(?, ?, ?)
        """, data.predefined_activities)
    db_connection.commit()


def create_habit(title, recurrence, created_at):
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
    cur.execute("DELETE FROM habits WHERE uuid = ?", (uuid,))

