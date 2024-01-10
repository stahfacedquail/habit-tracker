import db


if __name__ == '__main__':
    db.connect()
    db.setup_tables()
    db.populate_starter_data()

