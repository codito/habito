# -*- coding: utf-8 -*-
"""Models for habito."""

from datetime import datetime
from peewee import *    # noqa

db = SqliteDatabase(None)


def setup(name):
    """Sets up the database."""
    db.init(name)
    db.connect()
    db.create_tables([HabitModel, ActivityModel], safe=True)


class BaseModel(Model):
    """Base model class for Habito."""

    class Meta:
        """Meta class for the model."""

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
