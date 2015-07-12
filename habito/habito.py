# -*- coding: utf-8 -*-
"""Simple command line based habits tracker."""

import click

from datetime import datetime
from peewee import *    # noqa


database_name = "/tmp/habito.db"
db = SqliteDatabase(None)


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
    created_date = DateField()
    frequency = IntegerField(default=1)
    quantum = DoubleField()
    units = CharField()
    magica = TextField()
    active = BooleanField(default=True)

    def __str__(self):
        """String representation for a habit."""
        return "{0}\t{1}".format(self.frequency, self.name)


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
    update_date = DateTimeField()

    class Meta:
        database = db


@click.group()
def cli():
    """Habito - a simple command line habit tracker."""
    db.init(database_name)
    db.connect()
    db.create_tables([HabitModel, ActivityModel], safe=True)


@cli.command()
def list():
    """List all tracked habits."""
    for habit in HabitModel.select():
        click.echo(habit)


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
    print(ActivityModel._meta.database.database)
    activity = ActivityModel.create(for_habit=habit,
                                    quantum=quantum,
                                    update_date=datetime.now())
    click.echo("Added", nl=False)
    click.secho("{0} {1}".format(activity.quantum, habit.units),
                nl=False, fg='green')
    click.echo(" to habit")
    click.secho(habit.name, fg='green')


if __name__ == "__main__":
    cli()
