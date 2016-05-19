# -*- coding: utf-8 -*-
"""Simple command line based habits tracker."""

import click

from datetime import datetime, timedelta
from os import path, mkdir
from peewee import *    # noqa


database_name = path.join(click.get_app_dir("habito"), "habito.db")
db = SqliteDatabase(None)
TERMINAL_WIDTH, TERMINAL_HEIGHT = click.get_terminal_size()

class BaseModel(Model):

    """Base model class for Habito."""

    class Meta:
        database = db


class HabitModel(BaseModel):

    """Represents a single habit.

    Attributes:
        name (str): Description of the habit.
        created_date (datetime): Date on which the habit was added.
        quantum (float): Amount for the habit.
        frequency (int): Data input frequency in numbers of days. (Default: 1)
        units (str): Units of the quantum.
        magica (str): Why is this habit interesting?
        active (bool): True if the habit is active
    """

    name = CharField()
    created_date = DateField(default=datetime.now())
    frequency = IntegerField(default=1)
    quantum = DoubleField()
    units = CharField()
    magica = TextField()
    active = BooleanField(default=True)


class ActivityModel(BaseModel):

    """Updates for a Habit.

    Attributes:
        for_habit (int): Id of the Habit. Foreign key.
        update_date (date): Date time of the update.
        quantum (float): Amount for the habit.
    """

    for_habit = ForeignKeyField(HabitModel, related_name="activities",
                                index=True)
    quantum = FloatField()
    update_date = DateTimeField(default=datetime.now())


@click.group()
def cli():
    """Habito - a simple command line habit tracker."""
    if not path.exists(click.get_app_dir("habito")):
        mkdir(click.get_app_dir("habito"))
    db.init(database_name)
    db.connect()
    db.create_tables([HabitModel, ActivityModel], safe=True)


@cli.command()
def list():
    """List all tracked habits."""
    from terminaltables import SingleTable
    from textwrap import wrap

    nr_of_dates = TERMINAL_WIDTH//10 - 2
    if nr_of_dates < 1:
        click.echo("Your terminal window is too small. Please make it wider and try again")
        raise SystemExit(1)

    table_title = ["Habit", "Goal"]
    for d in range(0, nr_of_dates): 
        date_mod = datetime.today() - timedelta(days=d)
        table_title.append("{0}/{1}".format(date_mod.month, date_mod.day))

    table_rows = [table_title]
    for habit in HabitModel.select():
        habit_row = [str(habit.id) + ": " + habit.name, str(habit.quantum)]
        for d in range(0, nr_of_dates): 
            quanta = 0.0
            column_text = u'\u2717'
            date_mod = datetime.today() - timedelta(days=d)
            activities_on_date = ActivityModel.select()\
                .where((ActivityModel.for_habit == habit) &
                       (ActivityModel.update_date.year == date_mod.year) &
                       (ActivityModel.update_date.month == date_mod.month) &
                       (ActivityModel.update_date.day == date_mod.day))

            for a in activities_on_date:
                quanta += a.quantum

            if quanta >= habit.quantum:
                column_text = u'\u2713'

            habit_row.append("{0} ({1})".format(column_text, quanta))

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
    click.echo("You have commited to ", nl=False)
    click.secho("{0} {1}".format(quantum, units), nl=False, fg='green')
    click.echo(" of ")
    click.secho("{0}".format(habit_name), fg='green', nl=False)
    click.echo(" every day!")
    HabitModel.create(name=habit_name,
                      created_date=datetime.now(), quantum=quantum,
                      units=units, magica="")

@cli.command()
@click.argument("id", type=click.INT)
@click.option('--name', '-n', help="The new name (leave empty to leave unchanged)")
@click.option('--quantum', '-q', help="The new quantum (leave empty to leave unchanged)", type=click.FLOAT)
def edit(id, name, quantum):
    try:
        habit = HabitModel.get(HabitModel.id == id)
    except DoesNotExist:
        click.echo("The habit you're trying to edit does not exist!")
        raise SystemExit(1)
    habit.name = name.strip() or habit.name
    habit.quantum = quantum or habit.quantum
    habit.save()
    click.echo("Habit with id {} has been saved with name: {} and quantum: {}".format(id, habit.name, habit.quantum))


@cli.command()
@click.argument("id", type=click.INT)
@click.option("--keeplogs", is_flag=True, default=False)
def delete(id, keeplogs):
    try:
        habit = HabitModel.get(HabitModel.id == id)
    except DoesNotExist:
        click.echo("The habit you want to remove does not seem to exist!")
        raise SystemExit(1)
    confirm = click.prompt("Are you sure you want to delete habit {}: {} (this cannot be undone!)".format(habit.id, habit.name))
    if confirm:
        click.echo("Habit {}: {} has been deleted!".format(habit.id, habit.name))
        if not keeplogs:
            ad = ActivityModel.delete().where(ActivityModel.for_habit == habit.id)
            ad.execute()
        habit.delete_instance()
    else:
        click.echo("Habit {}: {} has not been deleted!".format(habit.id, habit.name))


@cli.command()
@click.argument("name", nargs=-1)
@click.option("--quantum", "-q", help="Quanta of data for the day",
              prompt=True)
def checkin(name, quantum):
    """Commit data for a habit."""
    query = ' '.join(name)
    habits = HabitModel.select().where(HabitModel.name.regexp(query))
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
    activity = ActivityModel.create(for_habit=habit,
                                    quantum=quantum,
                                    update_date=datetime.now())
    click.echo("Added ", nl=False)
    click.secho("{0} {1}".format(activity.quantum, habit.units),
                nl=False, fg='green')
    click.echo(" to habit")
    click.secho(habit.name, fg='green')


if __name__ == "__main__":
    cli()
