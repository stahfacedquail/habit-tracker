import db
import analytics


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.connect()
    db.setup_tables()
    db.populate_starter_data()

    habits = analytics.get_habits()
    for h in habits:
        print(h)

    print("\nSORTED")
    sorted_habits = analytics.sort_habits(habits, "desc", "last_performed")
    for h in sorted_habits:
        print(h)

    print("\nFILTERED")
    filtered_habits = analytics.filter_habits(habits, "recurrence", "weekly")
    for h in filtered_habits:
        print(h)

