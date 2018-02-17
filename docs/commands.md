# Command reference

We learnt day-to-day usage of habito in the [quickstart][habito-quickstart]
tutorial. Now let's dive deeper into the various command supported by habito.

[habito-quickstart]: index.md#quickstart

## Add
Add command (`habito add`) informs habito to track a new habit. A habit has
three aspects:

- A simple and easy to remember name
- A metric or unit for measuring the habit. E.g. miles if you're tracking daily
  runs
- A daily target for the habit. E.g. 3 miles daily

### Syntax
```
Usage: habito add [OPTIONS] [NAME]... QUANTUM

  Add a habit.

Options:
  -u, --units TEXT  Units of data.
  --help            Show this message and exit.
```

- `NAME` is the name to identify a habit
- `QUANTUM` is the daily target for the habit
- `--units` specifies the measurement unit for the habit

### Examples
(1) Add a habit

```sh
> habito add running 3
You have commited to 3.0 units of running every day!
```

(2) Add a habit specifying units

```sh
> habito add running 3 -u miles
You have commited to 3.0 miles of running every day!
```

## List

Legend:

- <span style="color:green">■</span> indicates we have met the goal for that
  day!
- ■ implies some activity on a day, but goal is not met
- □ implies no activity for the habito on a day


## Checkin
`checkin` command is used to update progress on the tracked habits.

### Syntax
```
Usage: habito checkin [OPTIONS] [NAME]...

  Commit progress for a habit.

Options:
  -r, --review         Update activity for all tracked habits.
  -d, --date TEXT      Date of activity in mm/dd format (defaults to today).
  -q, --quantum FLOAT  Progress for the day.
  --help               Show this message and exit.
```

- `NAME` is the habit name. Habito uses a simple regex match, so you need to
  provide an approximately unique string to identify the habit. E.g. `wri` for
  `writing`. Note that `checkin` will warn if multiple habits match.
- `--review` enables review mode. Habito iterates through all habits and
  prompts for an update on it. Doesn't require `NAME` or `quantum` arguments.
- `--date` can be used to specify a date for an update. E.g. 8th October is
  10/8 (mm/dd format).
- `--quantum` specifies progress data (float). E.g. 10.0.

### Examples
(1) Update progress for a single habit

```sh
> habito checkin writ -q 10.0
Added 10.0 words to habit writing for Mon Feb 12 2018.
```

(2) Update progress for single habit specifying date

```sh
# Today is 12th Feb, 2018
> habito checkin writ -q 10.0 -d 2/8
Added 10.0 words to habit writing for Thu Feb 08 2018.

# Habito assumes a past date if a future date is provided
> habito checkin writ -q 10.0 -d 4/8
Added 10.0 words to habit writing for Sat Apr 08 2017.
```

(3) Review all habits and update progress

We will skip update for `writing` habit in below session. Date of update is 9th
Feb, 2018 (2/9 in mm/dd format).

```sh
# Today is 12th Feb, 2018
> habito checkin -r -d 2/9
Please update progress of habits for Fri Feb 09 2018:
(Press `enter` if you'd like to skip update for a habit.)
  - writing (Goal: 750.0):
  - daily walk (Goal: 1.0): 1
  - read fiction daily (Goal: 15.0): 15
  - code everyday (Goal: 1.0): 1
```
