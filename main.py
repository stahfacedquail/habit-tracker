from modules import db
from modules.cli.home import show_home_menu

if __name__ == '__main__':
    db.connect()
    # TODO: Only do this if there's nothing yet
    db.setup_tables()
    db.populate_starter_data()
    show_home_menu(True)
