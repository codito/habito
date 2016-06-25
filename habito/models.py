# -*- coding: utf-8 -*-
"""Models for habito."""

from datetime import datetime, timedelta
from peewee import *    # noqa

db = SqliteDatabase(None)


def setup(name):
    """Set up the database."""
    db.init(name)
    db.connect()
    db.create_tables([HabitModel, ActivityModel], safe=True)


def get_activities(days):
    """Get activities of habits for specified days.

    Args:
        days (int): Number of days of activities to fetch.

    Returns:
        List of habits with the activities.
    """
    if days < 0:
        raise ValueError("Days should be a positive integer.")

    from_date = datetime.now() - timedelta(days=days)
    habits = HabitModel.select()
    activities = ActivityModel.select()\
        .where(ActivityModel.update_date > from_date)\
        .order_by(ActivityModel.update_date.desc())

    habits_with_activities = prefetch(habits, activities)
    return habits_with_activities


def get_daily_activities(days):
    """Get activities for all habits grouped by day for specified days.

    Args:
        days (int): Number of days of activities to fetch.

    Returns:
        Tuple of habit and list of daily activities. Daily activities are the
        sum of all activities for the habit for the day.

        E.g. [(habit, [(day1, activity), (day2, activity)..]), ..]
    """
    habits_with_activities = get_activities(days)
    daily_habits = []
    for habit in habits_with_activities:
        habit_data = []

        activity_index = 0
        activities = habit.activities_prefetch
        for day in range(0, days):
            quanta = 0.0
            if activity_index < len(activities):
                a = activities[activity_index]
            else:
                a = None

            # Assumes the data is sorted by date
            for_date = datetime.today() - timedelta(days=day)
            if a is None or a.update_date.date() != for_date.date():
                # We didn't find any data for the day
                quanta = None
            else:
                # Sum all activities for a day
                while a.update_date.date() == for_date.date():
                    quanta += a.quantum
                    activity_index += 1
                    if activity_index >= len(activities):
                        break
                    a = activities[activity_index]

            # Save the data for day
            habit_data.append((day, quanta))

        daily_habits.append((habit, habit_data))

    return daily_habits


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
