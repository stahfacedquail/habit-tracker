# Overview
This is a habit-tracking application, designed to help you keep track of a set of daily or weekly habits.  In it, you can create a habit, mark it as done, and view statistics about that habit or all the habits in your collection.

## Install dependencies
`pip3 install -r requirements.txt`

## Run the application
`python3 main.py`

### Creating a habit
1. Run the application, and you will be presented with the Home menu.
2. Select Option 1, "Create a new habit".
3. You will be prompted to enter the title of the habit.  Once you've done that, press Enter.
4. You will be prompted to indicate whether you want to perform the habit daily or weekly.  Use your arrows to choose your desired recurrence, and then press Enter.
5. You will get a success message indicating that your new habit has been created.  You can then press any key to continue.

## Run unit tests
`pytest`