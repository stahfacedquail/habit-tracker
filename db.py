import sqlite3
from uuid import uuid4

# global database connection for the application
db = None


def connect():
    global db
    db = sqlite3.connect("main.db")


def create_tables():
    if db is None:
        return

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
    data = [
        (str(uuid4()), "Jog", "daily"),
        (str(uuid4()), "Phone parents", "weekly"),
        (str(uuid4()), "Read a novel", "daily"),
        (str(uuid4()), "Journal", "weekly"),
        (str(uuid4()), "isiXhosa lesson", "weekly")
    ]
    cur.executemany("""
        INSERT INTO habits(uuid, title, recurrence)
        VALUES (?, ?, ?)
    """, data)
    db.commit()

