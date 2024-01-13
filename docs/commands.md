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

List command (`habito list`) shows the activities on the habits tracked by
habito. Habito keeps an account of several aspects of a habit:

- Activities for a habit. An activity is just a check-in, an update on the
  habit for a particular day.
- Multiple check-ins for a day are supported, habito aggregates these by day for
  reporting.
- Habito supports [Don't break the chain][no-break-chain] principle with
  _Streaks_. A streak represents **continuous set of days** where you've
  exceeded the target set for a habit.

[no-break-chain]: https://lifehacker.com/281626/jerry-seinfelds-productivity-secret

### Syntax

```
Usage: habito list [OPTIONS]

  List all tracked habits.

Options:
  -l                        Long listing with date and quantum.
  -f, --format [csv|table]  Output format. Default is table.
  -d, --duration TEXT       Duration for the report. Default is 1 week. If
                            format is table, maximum duration is inferred from
                            the terminal width.
  --help                    Show this message and exit.
```

**CSV format** can be used to print habits and activities aggregated by day in
a comma separated value format. Default duration is 1 week. You can use a custom
duration with `-d "1 month"` for instance. Supports human-readable values. See
[dateparser](https://dateparser.readthedocs.io/en/latest/) docs for spec.

**Tabular format (default)**

Activity reporting follows below convention by default. Use the `-l` switch if
you'd like a date based view.

- <span style="color:green">■</span> indicates we have met the goal for that
  day!
- ■ implies some activity on a day, but goal is not met
- □ implies no activity for the habito on a day

### Examples

(1) List all tracked habits

```sh
> habito list
┌───────────────────────┬───────┬────────┬──────────────────────────┐
│ Habit                 │ Goal  │ Streak │ Activities               │
├───────────────────────┼───────┼────────┼──────────────────────────┤
│ 1: running            │ 3.0   │ 2 days │ ■ ■ □ □ ■ □ ■ ■ ■ □ ■ □  │
└───────────────────────┴───────┴────────┴──────────────────────────┘
```

(2) List habits with dates

```sh
> habito list -l
┌───────────────────────┬───────┬────────┬───────┬───────┬──────┬──────┬───────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
│ Habit                 │ Goal  │ Streak │ 2/18  │ 2/17  │ 2/16 │ 2/15 │ 2/14  │ 2/13 │ 2/12 │ 2/11 │ 2/10 │ 2/9  │ 2/8  │ 2/7  │
├───────────────────────┼───────┼────────┼───────┼───────┼──────┼──────┼───────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
│ 1: running            │ 3.0   │ 2 days │ 3.0   │ 3.1   │ None │ None │ 3.5   │ None │ 1.0  │ 1.0  │ 2.0  │ None │ 1.0  │ None │
└───────────────────────┴───────┴────────┴───────┴───────┴──────┴──────┴───────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘
```

(3) List habits in csv format

```sh
> habito list -l -f csv -d "3 days"

id,name,goal,units,date,activity
1,running,3.0,miles,2023-02-16,0.0
1,running,3.0,miles,2023-02-17,3.1
1,running,3.0,miles,2023-02-18,3.0
```

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
> habito checkin run -q 10.0
Added 10.0 miles to habit running for Mon Feb 12 2018.
```

(2) Update progress for single habit specifying date

```sh
# Today is 12th Feb, 2018
> habito checkin run -q 10.0 -d 2/8
Added 10.0 words to habit running for Thu Feb 08 2018.

# Habito assumes a past date if a future date is provided
> habito checkin run -q 10.0 -d 4/8
Added 10.0 words to habit running for Sat Apr 08 2017.
```

(3) Review all habits and update progress

We will skip update for `running` habit in below session. Date of update is 9th
Feb, 2018 (2/9 in mm/dd format).

```sh
# Today is 12th Feb, 2018
> habito checkin -r -d 2/9
Please update progress of habits for Fri Feb 09 2018:
(Press `enter` if you'd like to skip update for a habit.)
  - running (Goal: 3.0 miles):
  - read fiction daily (Goal: 15.0 minutes): 15
  - code everyday (Goal: 1.0 commits): 1
```

## Edit

Edit command (`habito edit`) allows updating habit metadata: name and quantum (the target goal).

### Syntax

```
Usage: habito edit [OPTIONS] ID

  Edit a habit.

Options:
  -n, --name TEXT      The new name (leave empty to leave unchanged)
  -q, --quantum FLOAT  The new quantum (leave empty to leave unchanged)
  --help               Show this message and exit.
```

- `ID` is the habit id (you can find it in `habito list` output)

### Examples

(1) Change a habit name

```sh
> habito edit 1 -n "run with joe"
Habit with id 9 has been saved with name: run with joe and quantum: 3.0.
```

(2) Change a habit name and quantum

```sh
> habito edit 1 -n "run with joe" -q 2.5
Habit with id 9 has been saved with name: run with joe and quantum: 2.5.
```

## Delete

Delete command (`habito delete`) removes the habit and activities from the data store.

### Syntax

```
Usage: habito delete [OPTIONS] ID

  Delete a habit.

Options:
  --keeplogs  Preserve activity logs for the habit.
  --help      Show this message and exit.
```

- `ID` is the habit id (you can find it in `habito list` output)

### Examples

(1) Delete a habit (keep the logs)

```sh
> habito delete 9 --keeplogs
Are you sure you want to delete habit 9: run with joe (this cannot be undone!) [y/N]: y
Habit 9: run with joe has been deleted!
```

(2) Delete a habit along with activities

```sh
> habito delete 9
Are you sure you want to delete habit 9: run with joe (this cannot be undone!) [y/N]: y
Habit 9: run with joe has been deleted!
```
