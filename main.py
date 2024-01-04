import db
from classes.habit import Habit


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.connect()
    db.setup_tables()
    # habit1 = Habit("Practise piano", "daily", "2023-05-28 18:57:19")
    # habit2 = Habit(title="Water plants", recurrence="weekly")
