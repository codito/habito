# -*- coding: utf-8 -*-
"""Simple command line based habits tracker."""

import click
import logging

from datetime import datetime, timedelta
from os import path, mkdir

import habito.models as models

logger = logging.getLogger("habito")
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

    nr_of_dates = TERMINAL_WIDTH // 10 - 4
    if nr_of_dates < 1:
        logger.debug("list: Actual terminal width = {0}.".format(click.get_terminal_size()[0]))
        logger.debug("list: Observed terminal width = {0}.".format(TERMINAL_WIDTH))
        click.echo("Your terminal window is too small. Please make it wider and try again")
        raise SystemExit(1)

    table_title = ["Habit", "Goal", "Streak"]
    for d in range(0, nr_of_dates):
        date_mod = datetime.today() - timedelta(days=d)
        table_title.append("{0}/{1}".format(date_mod.month, date_mod.day))

    table_rows = [table_title]
    for habit_data in models.get_daily_activities(nr_of_dates):
        habit = habit_data[0]
        habit_row = [str(habit.id) + ": " + habit.name, str(habit.quantum)]
        for daily_data in habit_data[1]:
            column_text = u'\u2717'
            date_mod = datetime.today() - timedelta(days=daily_data[0])
            quanta = daily_data[1]

            if quanta is not None and quanta >= habit.quantum:
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
@click.argument("id", type=click.INT)
@click.option('--name', '-n', help="The new name (leave empty to leave unchanged)")
@click.option('--quantum', '-q', help="The new quantum (leave empty to leave unchanged)", type=click.FLOAT)
def edit(id, name, quantum):
    """Edit a habit.

    Args:
        name (str): Name of the habit.
        quantum (float): Quantity of progress every day.
    """
    try:
        habit = models.Habit.get(models.Habit.id == id)
    except models.Habit.DoesNotExist:
        click.echo("The habit you're trying to edit does not exist!")
        raise SystemExit(1)
    habit.name = name.strip() or habit.name
    habit.quantum = quantum or habit.quantum
    habit.save()
    click.echo("Habit with id {} has been saved with name: {} and quantum: {}".format(id, habit.name, habit.quantum))


@cli.command()
@click.argument("id", type=click.INT)
@click.option("--keeplogs", is_flag=True, default=False,
              help="Preserve activity logs for the habit.")
def delete(id, keeplogs):
    """Delete a habit.

    Args:
        name (str): Name of the habit.
        quantum (float): Quantity of progress every day.
    """
    try:
        habit = models.Habit.get(models.Habit.id == id)
    except models.Habit.DoesNotExist:
        click.echo("The habit you want to remove does not seem to exist!")
        raise SystemExit(1)
    confirm = click.confirm("Are you sure you want to delete habit"
                            " {}: {} (this cannot be undone!)"
                            .format(habit.id, habit.name))
    if confirm:
        click.echo("Habit {}: {} has been deleted!".format(habit.id, habit.name))
        if not keeplogs:
            ad = models.Activity.delete().where(models.Activity.for_habit == habit.id)
            ad.execute()
        habit.delete_instance()
    else:
        click.echo("Habit {}: {} has not been deleted!".format(habit.id, habit.name))


@cli.command()
@click.argument("name", nargs=-1)
@click.option("--date", "-d", help="The date (defaults to today)", default=datetime.now().strftime("%m/%d"))
@click.option("--quantum", "-q", help="Quanta of data for the day",
              prompt=True)
def checkin(name, date, quantum):
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

    # Set a date for this checkin. Use past year if month/day is in future
    date = date.strip()
    d = datetime.strptime(date, "%m/%d").replace(year=datetime.now().year)
    update_date = d if d < datetime.now() else d.replace(year=d.year-1)
    habit = habits[0]

    # Create an activity for this checkin
    activity = models.Activity.create(for_habit=habit,
                                      quantum=quantum,
                                      update_date=update_date)

    # Update streak for the habit
    models.Summary.update_streak(habit)

    click.echo("Added ", nl=False)
    click.secho("{0} {1}".format(activity.quantum, habit.units),
                nl=False, fg='green')
    click.echo(" to habit")
    click.secho(habit.name, fg='green')
    click.echo("for date: ", nl=False)
    click.secho(date, fg='green')


if __name__ == "__main__":
    cli()
