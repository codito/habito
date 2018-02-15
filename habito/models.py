# -*- coding: utf-8 -*-
"""Models for habito."""

import logging
from datetime import datetime, timedelta
from peewee import *    # noqa
from playhouse import reflection
from playhouse.sqlite_ext import SqliteExtDatabase
from playhouse.migrate import SqliteMigrator, migrate

DB_VERSION = 2
db = SqliteExtDatabase(None, pragmas=(('foreign_keys', 'on'),),
                       regexp_function=True)
logger = logging.getLogger("habito.models")


def setup(name):
    """Set up the database."""
    db.init(name)
    db.connect()
    Migration(db).execute()


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
    habits = Habit.all_active()
    activities = Activity.select()\
        .where(Activity.update_date > from_date)\
        .order_by(Activity.update_date.desc())

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
        activities = habit.activities
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


class Config(BaseModel):
    """Database configuration.

    Attributes:
        name (str): Name of the setting
        value (str): Value

    """

    name = CharField(unique=True)
    value = CharField()


class Habit(BaseModel):
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

    @classmethod
    def add(cls, **query):
        """Add a habit.

        Args:
            query (kwargs): List of fields and values.

        Returns:
            A Habit.

        """
        habit = cls.create(**query)
        Summary.create(for_habit=habit,
                       target=0,
                       target_date=datetime.now(),
                       streak=0)
        return habit

    @classmethod
    def all_active(cls):
        """Add a habit.

        Returns:
            All active habits.

        """
        return cls.select().where(Habit.active)


class Activity(BaseModel):
    """Updates for a Habit.

    Attributes:
        for_habit (int): Id of the Habit. Foreign key.
        update_date (date): Date time of the update.
        quantum (float): Amount for the habit.

    """

    for_habit = ForeignKeyField(Habit, related_name="activities",
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

    for_habit = ForeignKeyField(Habit, related_name="summary",
                                index=True)
    target = DoubleField()
    target_date = DateField()
    streak = IntegerField(default=0)

    @classmethod
    def update_streak(cls, habit):
        """Update streak for a habit.

        Args:
            habit (Habit): Habit to update.
        """
        # Check-in now supports past updates for upto 365 days
        # TODO need an index on date, this query will scan entire table
        summary = cls.get(for_habit=habit)
        activities = list((Activity
                           .select(Activity.update_date,
                                   fn.SUM(Activity.quantum).alias('total_quantum'))
                           .where(Activity.for_habit == habit)
                           .group_by(fn.date(Activity.update_date))
                           .order_by(Activity.update_date.desc())))

        if len(activities) == 0:
            return summary

        last_update = activities[0].update_date
        streak = 1
        for activity in activities[1:]:
            diff = last_update - activity.update_date
            if diff.days > 1 or activity.total_quantum < habit.quantum:
                break
            last_update = activity.update_date
            streak += 1

        summary.streak = streak
        summary.save()
        return summary

    def get_streak(self):
        """Humanize a streak to include days."""
        streak = str(self.streak) + " day"
        if self.streak != 1:
            streak += "s"
        return streak


class Migration:
    """Migrations for habito database."""

    # Error codes for the migrations
    error_codes = {-1: "not run",
                   0: "success",
                   1: "generic failure"}

    def __init__(self, database):
        """Create an instance of the migration.

        Args:
            database: database instance
        """
        self._db = database

    def get_version(self):
        """Get the database version.

        DB version is 0 if database is new.
        DB version is 1 if tables exist, but Config table is not available
        DB version is the actual version otherwise.

        Args:
            database (Database): peewee database instance

        Returns:
            Database version (int).

        """
        # Return version 1 if other tables (excluding Config) exist
        try:
            tables = reflection.introspect(self._db).model_names
            if len(tables) == 0:
                return 0
            if "config" not in tables:
                return 1
            version = int(Config.get(Config.name == "version").value)
        except Config.DoesNotExist:
            # Config table exists but version is not present
            version = 1
        return version

    def execute(self, list_only=False):
        """Migrate the database schema to latest version."""
        # It's a new database if `act_ver=0`
        # Set current version to 0, we will only run migration_0
        act_ver = self.get_version()
        cur_ver = 0 if act_ver == 0 else DB_VERSION
        logger.debug("DB version: actual = {0}, current = {1}"
                     .format(act_ver, cur_ver))

        if cur_ver != 0 and act_ver == cur_ver:
            logger.debug("DB versions are same. Skip migration.")
            return {}

        def get_migration(version):
            return self.__getattribute__("_migration_{}".format(version))

        m = {x: (get_migration(x), -1) for x in range(act_ver, cur_ver+1)}
        if list_only:
            # List the migration and status without running
            return {f[0]: f[1][1] for f in m.items()}

        # Run the migrations and report their status
        return {f[0]: f[1][0]() for f in m.items()}

    def _migration_0(self):
        """Set latest state of the database schema."""
        self._db.create_tables([Config, Habit, Activity, Summary], safe=True)
        Config.create(name="version", value=str(DB_VERSION))
        return 0

    def _migration_1(self):
        """Apply migration #1."""
        tables = reflection.introspect(self._db).model_names
        migrator = SqliteMigrator(self._db)
        if "habitmodel" in tables and "activitymodel" in tables:
            with self._db.transaction():
                migrate(
                    migrator.rename_table("habitmodel", "habit"),
                    migrator.rename_table("activitymodel", "activity"))
            logger.debug("Migration #1: Renamed habit, activity tables.")

        # Create new tables
        self._db.create_tables([Config, Summary], safe=True)
        logger.debug("Migration #1: Created tables.")

        # Set DB version
        Config.insert(name="version", value="1").on_conflict("replace").execute()
        logger.debug("Migration #1: DB version updated to 1.")

        # Update summaries
        for h in Habit.select():
            activities = Activity.select()\
                                 .where(Activity.for_habit == h)\
                                 .order_by(Activity.update_date.asc())
            streak = 0
            if len(activities) != 0:
                last_date = activities[0].update_date
                for a in activities:
                    delta = last_date - a.update_date
                    if abs(delta.days) > 1:
                        break
                    streak += 1
                    last_date = a.update_date

            # Update summary for the habit
            s = Summary.get_or_create(for_habit=h, target=0,
                                      target_date=h.created_date)
            s[0].streak = streak
            s[0].save()
        logger.debug("Migration #1: Summary updated for habits.")
        return 0

    def _migration_2(self):
        """Apply migration #2.

        This is a dummy migration step.
        """
        # Set DB version
        Config.insert(name="version", value="2").on_conflict("replace").execute()
        logger.debug("Migration #2: DB version updated to 2.")
        return 0
