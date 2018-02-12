# Command reference

## Add

## List

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
