import sqlite3
import data

# global database connection for the application
db = None


def connect(db_name="main.db"):
    global db
    db = sqlite3.connect(db_name)


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

