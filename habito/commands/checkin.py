# -*- coding: utf-8 -*-
"""Habito checkin command."""
from datetime import datetime
from sys import float_info

import click

from habito import models


@click.command()
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
