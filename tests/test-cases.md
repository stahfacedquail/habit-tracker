# TEST CASES

## `classes/activity.py`
- Initialisation: creating from scratch
    - with performed_at
    - without performed_at
- Initialisation: from db record
- To string

## `classes/habit.py`
- Initialisation: creating from scratch
    - with created_at
    - without created_at
- Initialisation: using uuid
- Initialisation: from db ({ habit: (...), activities: [...] })
- Get date last performed
    - No activities
    - Has activities
    - Multiple activities on last period performed
        - daily habit
        - weekly habit
- Get interval label
    - daily habit
    - weekly habit
    - count != 1
- To string
    - Habit that has activities
    - Habit that doesn't have activities
- Perform habit
    - with performed_at
    - without performed_at
- Delete habit
    - without activities
    - with activities
- Get all streaks
    - no streaks
    - default sorting (date, most recent to least recent)
    - sort by date, least recent to most recent
    - sort by length, longest to shortest
    - sort by length, shortest to longest
    - multiple activities in a period
        - as part of a streak (choose last performance to be end of streak)
        - as part of a streak (choose 1st performance to start streak)
        - as part of a streak (in the middle -- focus on length being correct)
        - standalone (not part of a streak -- should not be considered a streak)
- Get latest streak
    - no streak
        - no streak ever
        - has performed activity in previous period
        - has performed activity in current period
    - multiple activities in a period
        - in an old streak (which is the most recent)
            - at start of streak
            - at end of streak
            - in middle of streak (check streak length correct)
        - in previous period
            - no other streak / old streak
            - ongoing streak
        - in current period
            - no other streak / old streak
            - ongoing streak
    - has old streak
        - is the latest
        - has performed activity previous period
        - has performed activity current period
- Get number of times completed
    - no activities
    - single completion per period
    - multiple completions in a period
- Get completion rate
    - no activities
    - single completion per period
    - multiple completions in a period
    - closed date range
    - open date range
        - start but no end
        - end but no start

## `modules/analytics.py`
- Get habits (two habits, one with activities, the other without)
    - without today explicitly specified
    - with today explicitly specified
- Sort habits
    - Happy path, e.g. sort by number of periods performed in ascending order
    - Happy path, e.g. sort by latest streak length in descending order
    - Last performed at where habits include a None value
    - Title with mixed cases starting the title
- Filter habits
    - recurrence == "daily", returns results
    - recurrence == "weekly", returns no results

## `modules/db.py`
- Create habit
    - without created_at
    - with created_at
- Create activity
    - without created_at
    - with created_at
- Get habit
    - with activities
    - without activities
- Delete habit
    - without activities
    - with activities
- Get all habits (three habits - has activities, doesn't, has)
- Get all habits abridged

## `modules/utils.py`
- Get as local time (provide a GMT time, return the equivalent time in a certain timezone)
- Get as GMT (provide a time in a certain timezone, return that time as GMT)
- Format date for db (provide datetime string in a certain timezone, return datetime string in GMT)
- To datetime (returns datetime object wrt local timezone)
    - input a local time
    - input a GMT time
- To date-only string (input any datetime object)
- Get start of day (input any datetime object)
- Get number of days from, to
    - Same day, not inclusive
    - Same day, inclusive
    - Multiple days, not inclusive
    - Multiple days, inclusive
    - Less than 24 hours between (end) and (end - 1)
- Get number of weeks from, to
    - Same week, not inclusive
    - Same week, inclusive
    - Multiple weeks, not inclusive
    - Multiple weeks, inclusive
    - Less than 7 days between (end) and (end - 1), but fall in different weeks
- Get week start
    - Input Monday date
    - Input non-Monday date
- Add interval
    - Add 1 day
    - Add 3 weeks
- Group activities by performance period 
  - (Separate tests for daily habits and weekly habits)
  - Happy path
  - No activities
  - Multiple performances in a period
  - Date range filter:
      - closed range
      - open range
          - no start
          - no end
- Get accurate streak parameters
    - (Separate tests for daily, weekly habits)
    - Start and end date are on different dates
    - Start and end date are on same date
- Get date range for past week
- Get past month date range
    - Happy path (e.g. input: 15 March)
    - Mismatch (e.g. input: 31 March)
    - January
        - Happy (e.g. 3 January)
        - Mismatch (e.g. 31 January)
- Get last 6 months date range
    - Happy (e.g. 9 September)
    - Mismatch (e.g. 31 August)
    - First half of year
        - Happy (e.g. 14 April)
        - Mismatch (e.g. 30 March)