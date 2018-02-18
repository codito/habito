# -*- coding: utf-8 -*-
"""Simple command line based habits tracker."""

import click
import logging

from datetime import datetime, timedelta
from os import path, mkdir
from sys import float_info

import habito.models as models

logger = logging.getLogger("habito")
database_name = path.join(click.get_app_dir("habito"), "habito.db")
TERMINAL_WIDTH, TERMINAL_HEIGHT = click.get_terminal_size()

TICK = u"\u25A0"    # tick - 2713, black square - 25A0, 25AA, 25AF
CROSS = u"\u25A1"   # cross - 2717, white square - 25A1, 25AB, 25AE
PARTIAL = u"\u25A0"    # tick - 2713, black square - 25A0, 25AA, 25AF


@click.group()
def cli():
    """Habito - a simple command line habit tracker."""
    if not path.exists(click.get_app_dir("habito")):
        mkdir(click.get_app_dir("habito"))
    models.setup(database_name)


@cli.command()
@click.option("-l", is_flag=True, help="Long listing with date and quantum.")
def list(l):
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
    minimal = not l
    if minimal:
        table_title.append("Activities")
    else:
        for d in range(0, nr_of_dates):
            date_mod = datetime.today() - timedelta(days=d)
            table_title.append("{0}/{1}".format(date_mod.month, date_mod.day))

    table_rows = [table_title]
    for habit_data in models.get_daily_activities(nr_of_dates):
        habit = habit_data[0]
        habit_row = [str(habit.id) + ": " + habit.name, str(habit.quantum)]
        progress = ""
        for daily_data in habit_data[1]:
            column_text = CROSS
            quanta = daily_data[1]

            if quanta is not None:
                column_text = click.style(PARTIAL)
                if quanta >= habit.quantum:
                    column_text = click.style(TICK, fg="green")
            if minimal:
                progress += column_text + " "
            else:
                habit_row.append(quanta)
        if minimal:
            habit_row.append(progress)

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
    """Add a habit."""
    habit_name = ' '.join(name)
    models.Habit.add(name=habit_name,
                     created_date=datetime.now(),
                     quantum=quantum,
                     units=units,
                     magica="")

    msg_unit = click.style("{0} {1}".format(quantum, units), fg='green')
    msg_name = click.style("{0}".format(habit_name), fg='green')
    click.echo("You have commited to {0} of {1} every day!"
               .format(msg_unit, msg_name))


@cli.command()
@click.argument("id", type=click.INT)
@click.option('--name', '-n',
              help="The new name (leave empty to leave unchanged).")
@click.option('--quantum', '-q',
              type=click.FLOAT,
              help="The new quantum (leave empty to leave unchanged).")
def edit(id, name, quantum):
    """Edit a habit."""
    try:
        habit = models.Habit.get(models.Habit.id == id)
    except models.Habit.DoesNotExist:
        click.echo("The habit you're trying to edit does not exist!")
        raise SystemExit(1)
    habit.name = name.strip() or habit.name
    habit.quantum = quantum or habit.quantum
    habit.save()

    msg_id = click.style(str(habit.id), fg='green')
    msg_name = click.style(habit.name, fg='green')
    msg_quantum = click.style(str(habit.quantum), fg='green')
    click.echo("Habit with id {} has been saved with name: {} and quantum: {}."
               .format(msg_id, msg_name, msg_quantum))


@cli.command()
@click.argument("id", type=click.INT)
@click.option("--keeplogs", is_flag=True, default=False,
              help="Preserve activity logs for the habit.")
def delete(id, keeplogs):
    """Delete a habit."""
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
            models.Activity.delete().where(models.Activity.for_habit ==
                                           habit.id).execute()
            models.Summary.delete().where(models.Summary.for_habit ==
                                          habit.id).execute()
            habit.delete_instance()
        else:
            habit.active = False
            habit.save()
    else:
        click.echo("Habit {}: {} has not been deleted!".format(habit.id, habit.name))


@cli.command()
@click.argument("name", nargs=-1)
@click.option("--review", "-r", is_flag=True,
              help="Update activity for all tracked habits.")
@click.option("--date", "-d",
              help="Date of activity in mm/dd format (defaults to today).",
              default=datetime.now().strftime("%m/%d"))
@click.option("--quantum", "-q", type=float, help="Progress for the day.")
def checkin(name, review, date, quantum):
    """Commit progress for a habit."""
    # Set a date for this checkin. Use past year if month/day is in future
    query = ' '.join(name)
    date = date.strip()
    d = datetime.strptime(date, "%m/%d").replace(year=datetime.now().year)
    update_date = d if d < datetime.now() else d.replace(year=d.year-1)
    update_date_str = update_date.strftime("%a %b %d %Y")

    def print_header(date_str):
        header = "Please update progress of habits for {0}:"
        click.echo(header.format(click.style(date_str, fg='green')))

    def get_quantum(habit, required=True):
        msg = "  - {0} (Goal: {1} {2})"

        # Keep prompting until we have a value if required is True
        value = None if required else float_info.max
        q = click.prompt(msg.format(habit.name, habit.quantum, habit.units),
                         type=float,
                         show_default=False,
                         default=value)
        if not required and q == value:
            return None
        return q

    def update_activity(habit, quantum, date):
        # Create an activity for this checkin
        activity = models.Activity.create(for_habit=habit,
                                          quantum=quantum,
                                          update_date=update_date)

        # Update streak for the habit
        models.Summary.update_streak(habit)
        return activity

    # Review mode: iterate through all habits
    if review:
        print_header(update_date_str)
        click.echo("(Press `enter` if you'd like to skip update for a habit.)")
        for h in models.Habit.all_active():
            q = get_quantum(h, required=False)
            if q is not None:
                update_activity(h, q, update_date)
        return

    # Non review mode: checkin a single habit
    if query == "":
        click.echo("No habit specified, no progress updated.")
        click.echo("Try 'habito checkin <habit_name>'?")
        return
    habits = models.Habit.all_active().where(models.Habit.name.regexp(query))
    if habits.count() == 0:
        error = "No habit matched the name '{0}'.".format(query)
        click.secho(error, fg='red')
        return
    elif habits.count() > 1:
        error = ("More than one habits matched the name '{0}'. "
                 "Don't know which to update.").format(query)
        click.secho(error, fg='red')
        for h in habits:
            click.echo("- {0}".format(h.name))
        click.echo("Try a different filter, or `habito checkin --review`.")
        return

    # Now add the activity for the chosen habit
    habit = habits[0]
    if quantum is None:
        print_header(update_date_str)
        quantum = get_quantum(habit, required=True)
    activity = update_activity(habit, quantum, update_date)

    act_msg = click.style("{0} {1}".format(activity.quantum, habit.units),
                          fg='green')
    act_date = click.style(update_date_str, fg='green')
    habit_msg = click.style("{0}".format(habit.name), fg='green')
    click.echo("Added {0} to habit {1} for {2}.".format(act_msg, habit_msg, act_date))


if __name__ == "__main__":
    cli()
