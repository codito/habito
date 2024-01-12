# -*- coding: utf-8 -*-
"""Tests for habito models."""

import pytest
from datetime import datetime

import habito.models as models
from tests import HabitoTestCase


class ModelTests(HabitoTestCase):
    def setUp(self):
        models.setup(":memory:")

    def test_setup_creates_tables(self):
        assert len(models.db.get_tables()) == 4

    def test_get_activities_raises_for_invalid_days(self):
        with pytest.raises(ValueError):
            models.get_activities(-1)

    def test_get_activities_should_return_empty_for_no_activities(self):
        self.create_habit()

        ha = models.get_activities(1)

        assert len(ha[0].activities) == 0

    def test_get_activities_should_return_activities_within_days(self):
        habit = self.create_habit()
        self.add_activity(habit, 20.0)
        self.add_activity(habit, update_date=ModelTests.two_days_ago)

        h = models.get_activities(1)

        assert len(h[0].activities) == 1
        assert h[0].activities[0].quantum == 20.0

    def test_get_activities_should_return_activities_sorted(self):
        habit = self.create_habit()
        a1 = self.add_activity(habit, 20.0, ModelTests.one_day_ago)
        a2 = self.add_activity(habit, 1.0, ModelTests.two_days_ago)
        a3 = self.add_activity(habit, 10.0, ModelTests.one_day_ago)

        h = models.get_activities(3)

        assert h[0].activities == [a1, a3, a2]

    def test_get_daily_activities_should_return_activities_groups(self):
        habit = self.create_habit()
        self.add_activity(habit, 20.0, ModelTests.one_day_ago)
        self.add_activity(habit, 10.0, ModelTests.one_day_ago)
        self.add_activity(habit, 1.0, ModelTests.two_days_ago)

        h = models.get_daily_activities(2)

        assert len(h) == 1
        assert h[0][0] == habit
        assert h[0][1] == [(0, None), (1, 30.0)]

    def test_get_daily_activities_should_return_all_habits_activity(self):
        habit1 = self.create_habit()
        habit2 = self.create_habit("Habit 2", quantum=2)
        self.add_activity(habit1, 20.0, ModelTests.one_day_ago)
        self.add_activity(habit2, 10.0, ModelTests.one_day_ago)
        self.add_activity(habit1, 1.0, ModelTests.two_days_ago)

        h = models.get_daily_activities(3)

        assert len(h) == 2
        assert h[0][0] == habit1
        assert h[1][0] == habit2
        assert h[0][1] == [(0, None), (1, 20.0), (2, 1.0)]
        assert h[1][1] == [(0, None), (1, 10.0), (2, None)]


class MigrationTests(HabitoTestCase):
    def setUp(self):
        models.db.init(":memory:")
        models.db.connect()

        self.migration = models.Migration(models.db)

    # Version scenarios
    def test_get_version_returns_zero_if_db_doesnot_exist(self):
        version = self.migration.get_version()

        assert version == 0

    def test_get_version_returns_one_if_other_tables_exist(self):
        self._setup_db_exist_no_config()

        version = self.migration.get_version()

        assert version == 1

    def test_get_version_returns_one_if_key_doesnot_exist(self):
        self._setup_db_exist_config_version_doesnot_exist()

        version = self.migration.get_version()

        assert version == 1

    def test_get_version_returns_version_if_config_exists(self):
        self._setup_db_exist_config_version()

        version = self.migration.get_version()

        assert version == 2

    # Migration scenario: DB doesn't exist
    def test_execute_list_result_db_doesnot_exist(self):
        result = self.migration.execute(list_only=True)

        assert result == {0: -1}

    def test_execute_run_result_db_doesnot_exist(self):
        ver = str(models.DB_VERSION)

        result = self.migration.execute()

        assert result == {0: 0}
        assert models.Config.get(models.Config.name == "version").value == ver
        assert models.Habit.select().count() == 0
        assert models.Activity.select().count() == 0
        assert models.Summary.select().count() == 0

    # Migration scenario: DB is at version 1
    def test_execute_list_result_db_exist_without_config(self):
        self._setup_db_exist_no_config()

        result = self.migration.execute(list_only=True)

        assert result == {1: -1, 2: -1}

    def test_execute_run_result_db_exist_without_config(self):
        self._setup_db_exist_no_config()

        result = self.migration.execute()

        assert result == {1: 0, 2: 0}
        self._verify_row_counts_for_version_2()
        self._verify_summary_for_version_2()

    def test_execute_migration_1_to_2_is_idempotent(self):
        self._setup_db_exist_no_config()
        result = self.migration.execute()
        models.Config.update(value="1").where(models.Config.name == "version").execute()

        result = self.migration.execute()

        assert result == {1: 0, 2: 0}
        self._verify_row_counts_for_version_2()
        self._verify_summary_for_version_2()

    # Migration scenario: DB is at version 2
    def test_execute_list_result_db_exist_with_config(self):
        self._setup_db_exist_config_version()

        result = self.migration.execute(list_only=True)

        assert result == {}

    def test_execute_run_result_db_exist_with_config(self):
        self._setup_db_exist_config_version()

        result = self.migration.execute()

        assert result == {}

    # Fixtures for DB states
    def _setup_db_exist_no_config(self):
        """DB version 1 setup."""
        with open("tests/sql/01.sql", "r") as f:
            script = f.read()
            for s in script.split(";"):
                models.db.execute_sql(s + ";")

    def _setup_db_exist_config_version_doesnot_exist(self):
        """DB version 1 setup with error.

        Config table exists, but version key is not present.
        """
        models.db.create_tables([models.Config])

    def _setup_db_exist_config_version(self):
        """DB version 2 setup."""
        models.db.create_tables([models.Config])
        models.Config.create(name="version", value="2")

    # Validations for DB states
    def _verify_row_counts_for_version_2(self):
        ver = str(models.DB_VERSION)

        assert models.Config.get(models.Config.name == "version").value == ver
        assert models.Habit.select().count() == 2
        assert models.Activity.select().count() == 4
        assert models.Summary.select().count() == 2

    def _verify_summary_for_version_2(self):
        s1 = models.Summary.get(models.Summary.id == 1).streak
        s2 = models.Summary.get(models.Summary.id == 2).streak
        assert s1 == 2
        assert s2 == 1


class HabitTests(HabitoTestCase):
    def setUp(self):
        models.setup(":memory:")

    def tearDown(self):
        models.db.drop_tables(
            [models.Habit, models.Activity, models.Summary], safe=True
        )

    def test_habit_add_creates_a_habit(self):
        dummy_date = datetime.now()
        habit = models.Habit.add(
            name="Dummy Habit",
            created_date=dummy_date,
            quantum=1,
            units="dummy_units",
            magica="magica",
        )

        assert habit.name == "Dummy Habit"
        assert habit.created_date == dummy_date
        assert habit.quantum == 1
        assert habit.units == "dummy_units"
        assert habit.magica == "magica"
        assert habit.frequency == 1
        assert habit.active is True

    def test_habit_add_creates_a_summary_for_habit(self):
        habit = models.Habit.add(
            name="Dummy Habit", quantum=1, units="dummy_units", magica="magica"
        )

        summary = models.Summary.get(for_habit=habit)
        assert summary.streak == 0


class SummaryTests(HabitoTestCase):
    def setUp(self):
        models.setup(":memory:")

    def tearDown(self):
        models.db.drop_tables(
            [models.Habit, models.Activity, models.Summary], safe=True
        )

    def test_update_streak_sets_streak_unchanged_for_no_activities(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)

        summary = models.Summary.update_streak(habit)

        assert summary.streak == 2

    def test_update_streak_sets_streak_if_last_activity_is_not_today(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)
        self.add_activity(habit, update_date=SummaryTests.one_day_ago)

        summary = models.Summary.update_streak(habit)

        assert summary.streak == 1

    def test_update_streak_sets_streak_as_one_if_activity_is_today(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        assert summary.streak == 1

    def test_update_streak_sets_single_streak_if_more_activities_today(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)
        self.add_activity(habit, update_date=datetime.today())
        self.add_activity(habit, update_date=datetime.today())
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        assert summary.streak == 1

    def test_update_streak_counts_streak_for_continuous_activity(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)
        self.add_activity(habit, update_date=SummaryTests.two_days_ago)
        self.add_activity(habit, update_date=SummaryTests.two_days_ago)
        self.add_activity(habit, update_date=SummaryTests.one_day_ago)
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        assert summary.streak == 3

    def test_update_streak_sets_streak_as_one_for_irregular_activity(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)
        self.add_activity(habit, update_date=SummaryTests.two_days_ago)
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        assert summary.streak == 1

    def test_get_streak_should_add_days_for_zero_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=0)

        streak = habit.summary.get().get_streak()

        assert streak == "0 days"

    def test_get_streak_should_add_days_for_plural_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=20)

        streak = habit.summary.get().get_streak()

        assert streak == "20 days"

    def test_get_streak_should_add_days_for_one_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=1)

        streak = habit.summary.get().get_streak()

        assert streak == "1 day"
