def get_habits(columns: list[str]):
    """
    Fetch all the user's habits, displaying their titles and the `columns` specified.
    :param columns: The properties of the habits that must be computed (in some cases) and returned
    :return: A list of tuples, each tuple starting with the habit's titles and then the rest of the details stipulated
        by `columns`
    """
    # MANDATORY
    # Column 1 -> title
    # OPTIONAL
    # Column 2 -> created_at
    # Column 3 -> recurrence
    # Column 4 -> last_performed
    # Column 5 -> num times performed
    # Column 6 -> completion rate
    # Column 7 -> length of current streak


def sort_habits(habits: list[tuple], prop: str, order: str):
    """
    Sort the list of habit tuples.
    :param habits: A list of tuples each containing details about a habit
    :param prop: The property by which to sort the list, e.g. "completion_rate"
    :param order: "asc" or "desc", i.e. whether to sort by ascending or descending order
    :return: A new list of habit tuples, sorted as requested
    """
    pass


def filter_habits(habits: list[tuple], prop: str, value: any):
    """
    Show a subset of the list of habit tuples, filtered by a particular property.
    :param habits: A list of tuples each containing details about a habit
    :param prop: The property by which to filter the list.  Currently only available property is "recurrence_type".
    :param value: Only display habits whose value for the requested `prop` is `value`
    :return: A new list of habit tuples, filtered as requested
    """
    pass
