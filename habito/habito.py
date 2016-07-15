# -*- coding: utf-8 -*-
"""Simple command line based habits tracker."""

import click

from datetime import datetime, timedelta
from os import path, mkdir

import habito.models as models

database_name = path.join(click.get_app_dir("habito"), "habito.db")
TERMINAL_WIDTH, TERMINAL_HEIGHT = click.get_terminal_size()


@click.group()
def cli():
    """Habito - a simple command line habit tracker."""
    if not path.exists(click.get_app_dir("habito")):
        mkdir(click.get_app_dir("habito"))
    models.setup(database_name)


@cli.command()
def list():
    """List all tracked habits."""
    from terminaltables import SingleTable
    from textwrap import wrap

    nr_of_dates = TERMINAL_WIDTH // 10 - 3
    if nr_of_dates < 1:
        click.echo("Your terminal window is too small. Please make it wider and try again")
        raise SystemExit(1)

    table_title = ["Habit", "Goal", "Streak"]
    for d in range(0, nr_of_dates):
        date_mod = datetime.today() - timedelta(days=d)
        table_title.append("{0}/{1}".format(date_mod.month, date_mod.day))

    table_rows = [table_title]
    for habit_data in models.get_daily_activities(nr_of_dates):
        habit = habit_data[0]
        habit_row = [habit.name, str(habit.quantum)]
        for daily_data in habit_data[1]:
            column_text = u'\u2717'
            date_mod = datetime.today() - timedelta(days=daily_data[0])
            quanta = daily_data[1]

            if quanta is None or quanta >= habit.quantum:
                column_text = u'\u2713'
            habit_row.append("{0} ({1})".format(column_text, quanta))

        current_streak = habit.summary.get().get_streak()
        habit_row.insert(2, current_streak)
        table_rows.append(habit_row)

    table = SingleTable(table_rows)

    max_col_width = table.column_max_width(0)
    max_col_width = max_col_width if max_col_width > 0 else 20

    for r in table_rows:
        r[0] = '\n'.join(wrap(r[0], max_col_width))

    click.echo(table.table)


@cli.command()
@click.argument("name", nargs=-1)
@click.argument("quantum", type=click.FLOAT)
@click.option("--units", "-u", default="units", help="Units of data.")
def add(name, quantum, units):
    """Add a habit.

    Args:
        name (str): Name of the habit.
        quantum (float): Quantity of progress every day.
    """
    habit_name = ' '.join(name)
    models.Habit.add(name=habit_name,
                     created_date=datetime.now(),
                     quantum=quantum,
                     units=units,
                     magica="")

    click.echo("You have commited to ", nl=False)
    click.secho("{0} {1}".format(quantum, units), nl=False, fg='green')
    click.echo(" of ")
    click.secho("{0}".format(habit_name), fg='green', nl=False)
    click.echo(" every day!")


@cli.command()
@click.argument("name", nargs=-1)
@click.option("--quantum", "-q", help="Quanta of data for the day",
              prompt=True)
def checkin(name, quantum):
    """Commit data for a habit."""
    query = ' '.join(name)
    habits = models.Habit.select().where(models.Habit.name.regexp(query))
    if habits.count() == 0:
        error = "No tracked habits match the query '{0}'.".format(query)
        click.secho(error, fg='red')
        return
    elif habits.count() > 1:
        error = "More than one tracked habits match the query '{0}'."\
            .format(query)
        click.secho(error, fg='red')
        for h in habits:
            click.echo(h.name)
        return

    habit = habits[0]

    # Create an activity for this checkin
    activity = models.Activity.create(for_habit=habit,
                                      quantum=quantum,
                                      update_date=datetime.now())

    # Update streak for the habit
    models.Summary.update_streak(habit)

    click.echo("Added ", nl=False)
    click.secho("{0} {1}".format(activity.quantum, habit.units),
                nl=False, fg='green')
    click.echo(" to habit")
    click.secho(habit.name, fg='green')


if __name__ == "__main__":
    cli()
