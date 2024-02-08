from modules import db, cli

if __name__ == '__main__':
    db.connect()
    # TODO: Only do this if there's nothing yet
    db.setup_tables()
    db.populate_starter_data()
    cli.show_home_menu(True)
