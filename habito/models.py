# -*- coding: utf-8 -*-
"""Models for habito."""

from datetime import datetime, timedelta
from peewee import *    # noqa

db = SqliteDatabase(None)


def setup(name):
    """Set up the database."""
    db.init(name)
    db.connect()
    db.create_tables([HabitModel, ActivityModel, Summary], safe=True)


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
    quantum = DoubleField()
    update_date = DateTimeField(default=datetime.now())


class Summary(BaseModel):
    """Continuous metrics for a Habit.

    Attributes:
        for_habit (int): Id of the Habit. Foreign key.
        target (float): A target for the Habit. Computed from the quantum.
        target_date (date): Date for the target.
        streak (int): Current streak for a habit. Continuous activity
        constitutes a streak.
    """

    for_habit = ForeignKeyField(HabitModel, related_name="summary",
                                index=True)
    target = DoubleField()
    target_date = DateField()
    streak = IntegerField(default=0)

    @classmethod
    def update_streak(cls, habit):
        """Update streak for a habit.

        Args:
            habit (HabitModel): Habit to update.
        """
        last_two_activity = ActivityModel.select()\
            .where(ActivityModel.for_habit == habit)\
            .order_by(ActivityModel.update_date.desc())\
            .limit(2)

        summary = cls.get(for_habit=habit)

        def is_yesterday_activity(activity):
            yesterday = (datetime.today() - timedelta(days=1)).date()
            return activity.update_date.date() == yesterday

        def is_past_activity(activity):
            yesterday = (datetime.today() - timedelta(days=1)).date()
            return activity.update_date.date() < yesterday

        while True:
            # Streak is 0 if there are no activities
            if len(last_two_activity) == 0:
                summary.streak = 0
                break

            # Streak is 0 if no activity happened today or yesterday
            if is_past_activity(last_two_activity[0]):
                summary.streak = 0
                break

            # If the last activity was yesterday, there can be an
            # update today. Keep streak unchanged.
            if is_yesterday_activity(last_two_activity[0]):
                break

            # Great, the latest activity was today.
            if len(last_two_activity) == 1:
                # Today's activity is the only activity
                summary.streak = 1
                break

            # Set streak based on continuity in last two activities
            if is_yesterday_activity(last_two_activity[1]):
                summary.streak += 1
            elif is_past_activity(last_two_activity[1]):
                # There's no continuity in last two activities
                summary.streak = 1
            break

        summary.save()
        return summary

    def humanize(self):
        """Humanize a streak to include days."""
        streak = str(self.streak) + " day"
        if self.streak != 1:
            streak += "s"
        return streak
