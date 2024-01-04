from datetime import datetime
from db import create_habit


class Habit:

    def __init__(self, title, recurrence, created_at=None):
        self = create_habit(title, recurrence, created_at)
        print("Model")
        print(self)
