import db
from classes.habit import Habit


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.connect()
    db.setup_tables()
    db.populate_starter_data()
