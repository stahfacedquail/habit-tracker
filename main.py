from modules import db
from modules.cli.home import show_home_menu


if __name__ == '__main__':
    db.connect()
    setup_required = db.setup_tables()
    if setup_required:
        db.populate_starter_data()

    show_home_menu(True)
