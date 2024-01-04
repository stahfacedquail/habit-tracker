import sqlite3
import data
from utils import make_uuid

# global database connection for the application
db = None


def connect(db_name="main.db"):
    global db
    db = sqlite3.connect(db_name)


def setup_tables():
    cur = db.cursor()
    # clear old data
    cur.execute("DROP TABLE IF EXISTS recurrence_types")
    cur.execute("DROP TABLE IF EXISTS activities")
    cur.execute("DROP TABLE IF EXISTS habits")

    # create afresh
    cur.execute("CREATE TABLE recurrence_types(type TEXT PRIMARY KEY)")
    cur.execute("""
        INSERT INTO recurrence_types VALUES
            ("daily"),
            ("weekly")
    """)
    db.commit()

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
    cur.executemany("""
        INSERT INTO habits VALUES (?, ?, ?, ?)
    """, data.predefined_habits)
    db.commit()

    cur.execute("""
        CREATE TABLE activities(
            uuid TEXT PRIMARY KEY,
            habit TEXT NOT NULL,
            performed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit)
                REFERENCES habits(uuid)
        )
    """)
    cur.executemany("""
        INSERT INTO activities VALUES(?, ?, ?)
    """, data.predefined_activities)
    db.commit()


def create_habit(title, recurrence, created_at):
    cur = db.cursor()
    uuid = make_uuid()

    if created_at is None:
        cur.execute("""
            INSERT INTO habits(uuid, title, recurrence)
            VALUES(?, ?, ?)
        """, (uuid, title, recurrence))
    else:
        cur.execute("""
            INSERT INTO habits VALUES(?, ?, ?, ?)
        """, (uuid, title, recurrence, created_at))
    db.commit()
    cur.execute("""SELECT * FROM habits WHERE uuid = ?""", (uuid,))
    new_habit = cur.fetchone()
    print("DB")
    print(new_habit)
    return new_habit

