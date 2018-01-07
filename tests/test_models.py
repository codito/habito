# -*- coding: utf-8 -*-
"""Tests for habito models."""

from datetime import datetime
from sure import expect

import habito.models as models
from tests import HabitoTestCase


class ModelTests(HabitoTestCase):
    def setUp(self):
        models.setup(":memory:")

    def test_setup_creates_tables(self):
        expect(len(models.db.get_tables())).to.be(4)

    def test_get_activities_raises_for_invalid_days(self):
        ga = models.get_activities

        expect(ga).when.called_with(-1).to.throw(ValueError)

    def test_get_activities_should_return_empty_for_no_activities(self):
        self.create_habit()

        ha = models.get_activities(1)

        expect(ha[0].activities_prefetch).to.empty

    def test_get_activities_should_return_activities_within_days(self):
        habit = self.create_habit()
        self.add_activity(habit, 20.0)
        self.add_activity(habit, update_date=ModelTests.two_days_ago)

        h = models.get_activities(1)

        expect(h[0].activities_prefetch).to.have.length_of(1)
        expect(h[0].activities_prefetch[0].quantum).to.equal(20.0)

    def test_get_activities_should_return_activities_sorted(self):
        habit = self.create_habit()
        a1 = self.add_activity(habit, 20.0, ModelTests.one_day_ago)
        a2 = self.add_activity(habit, 1.0, ModelTests.two_days_ago)
        a3 = self.add_activity(habit, 10.0, ModelTests.one_day_ago)

        h = models.get_activities(3)

        expect(h[0].activities_prefetch).to.equal([a1, a3, a2])

    def test_get_daily_activities_should_return_activities_groups(self):
        habit = self.create_habit()
        self.add_activity(habit, 20.0, ModelTests.one_day_ago)
        self.add_activity(habit, 10.0, ModelTests.one_day_ago)
        self.add_activity(habit, 1.0, ModelTests.two_days_ago)

        h = models.get_daily_activities(2)

        expect(h).to.have.length_of(1)
        expect(h[0][0]).to.equal(habit)
        expect(h[0][1]).to.equal([(0, None), (1, 30.0)])

    def test_get_daily_activities_should_return_all_habits_activity(self):
        habit1 = self.create_habit()
        habit2 = self.create_habit("Habit 2", quantum=2)
        self.add_activity(habit1, 20.0, ModelTests.one_day_ago)
        self.add_activity(habit2, 10.0, ModelTests.one_day_ago)
        self.add_activity(habit1, 1.0, ModelTests.two_days_ago)

        h = models.get_daily_activities(3)

        expect(h).to.have.length_of(2)
        expect(h[0][0]).to.equal(habit1)
        expect(h[1][0]).to.equal(habit2)
        expect(h[0][1]).to.equal([(0, None), (1, 20.0), (2, 1.0)])
        expect(h[1][1]).to.equal([(0, None), (1, 10.0), (2, None)])


class MigrationTests(HabitoTestCase):
    def setUp(self):
        models.db.init(":memory:")
        models.db.connect()

        self.migration = models.Migration(models.db)

    # Version scenarios
    def test_get_version_returns_zero_if_db_doesnot_exist(self):
        version = self.migration.get_version()

        expect(version).to.eql(0)

    def test_get_version_returns_one_if_other_tables_exist(self):
        self._setup_db_exist_no_config()

        version = self.migration.get_version()

        expect(version).to.eql(1)

    def test_get_version_returns_one_if_key_doesnot_exist(self):
        self._setup_db_exist_config_version_doesnot_exist()

        version = self.migration.get_version()

        expect(version).to.eql(1)

    def test_get_version_returns_version_if_config_exists(self):
        self._setup_db_exist_config_version()

        version = self.migration.get_version()

        expect(version).to.eql(2)

    # Migration scenario: DB doesn't exist
    def test_execute_list_result_db_doesnot_exist(self):
        result = self.migration.execute(list_only=True)

        expect(result).to.eql({0: -1})

    def test_execute_run_result_db_doesnot_exist(self):
        ver = str(models.DB_VERSION)

        result = self.migration.execute()

        expect(result).to.eql({0: 0})
        expect(models.Config.get(models.Config.name == "version").value).to.eql(ver)
        expect(models.Habit.select().count()).to.eql(0)
        expect(models.Activity.select().count()).to.eql(0)
        expect(models.Summary.select().count()).to.eql(0)

    # Migration scenario: DB is at version 1
    def test_execute_list_result_db_exist_without_config(self):
        self._setup_db_exist_no_config()

        result = self.migration.execute(list_only=True)

        expect(result).to.eql({1: -1, 2: -1})

    def test_execute_run_result_db_exist_without_config(self):
        self._setup_db_exist_no_config()

        result = self.migration.execute()

        expect(result).to.eql({1: 0, 2: 0})
        self._verify_row_counts_for_version_2()
        self._verify_summary_for_version_2()

    def test_execute_migration_1_to_2_is_idempotent(self):
        self._setup_db_exist_no_config()
        result = self.migration.execute()
        models.Config.update(value="1").where(models.Config.name == "version").execute()

        result = self.migration.execute()

        expect(result).to.eql({1: 0, 2: 0})
        self._verify_row_counts_for_version_2()
        self._verify_summary_for_version_2()

    # Migration scenario: DB is at version 2
    def test_execute_list_result_db_exist_with_config(self):
        self._setup_db_exist_config_version()

        result = self.migration.execute(list_only=True)

        expect(result).to.eql({})

    def test_execute_run_result_db_exist_with_config(self):
        self._setup_db_exist_config_version()

        result = self.migration.execute()

        expect(result).to.eql({})

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
        models.db.create_table(models.Config)

    def _setup_db_exist_config_version(self):
        """DB version 2 setup."""
        models.db.create_table(models.Config)
        models.Config.create(name="version", value="2")

    # Validations for DB states
    def _verify_row_counts_for_version_2(self):
        ver = str(models.DB_VERSION)

        expect(models.Config.get(models.Config.name == "version").value).to.eql(ver)
        expect(models.Habit.select().count()).to.eql(2)
        expect(models.Activity.select().count()).to.eql(4)
        expect(models.Summary.select().count()).to.eql(2)

    def _verify_summary_for_version_2(self):
        s1 = models.Summary.get(models.Summary.id == 1).streak
        s2 = models.Summary.get(models.Summary.id == 2).streak
        expect(s1).to.eql(2)
        expect(s2).to.eql(1)


class HabitTests(HabitoTestCase):
    def setUp(self):
        models.setup(":memory:")

    def tearDown(self):
        models.db.drop_tables([models.Habit, models.Activity, models.Summary],
                              safe=True)

    def test_habit_add_creates_a_habit(self):
        dummy_date = datetime.now()
        habit = models.Habit.add(name="Dummy Habit",
                                 created_date=dummy_date,
                                 quantum=1,
                                 units="dummy_units",
                                 magica="magica")

        expect(habit.name).to.equal("Dummy Habit")
        expect(habit.created_date).to.equal(dummy_date)
        expect(habit.quantum).to.equal(1)
        expect(habit.units).to.equal("dummy_units")
        expect(habit.magica).to.equal("magica")
        expect(habit.frequency).to.equal(1)
        expect(habit.active).to.true

    def test_habit_add_creates_a_summary_for_habit(self):
        habit = models.Habit.add(name="Dummy Habit",
                                 quantum=1,
                                 units="dummy_units",
                                 magica="magica")

        summary = models.Summary.get(for_habit=habit)
        expect(summary.streak).to.equal(0)


class SummaryTests(HabitoTestCase):
    def setUp(self):
        models.setup(":memory:")

    def tearDown(self):
        models.db.drop_tables([models.Habit, models.Activity, models.Summary],
                              safe=True)

    def test_update_streak_sets_streak_as_zero_for_no_activities(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(0)

    def test_update_streak_doesnot_set_streak_if_last_activity_yesterday(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)
        self.add_activity(habit, update_date=SummaryTests.one_day_ago)

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(2)

    def test_update_streak_sets_streak_as_one_if_only_activity_was_today(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(1)

    def test_update_streak_doesnot_set_streak_if_more_activities_today(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=2)
        self.add_activity(habit, update_date=datetime.today())
        self.add_activity(habit, update_date=datetime.today())
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(2)

    def test_update_streak_increments_streak_for_regular_activity(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)
        self.add_activity(habit, update_date=SummaryTests.two_days_ago)
        self.add_activity(habit, update_date=SummaryTests.one_day_ago)
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(11)

    def test_update_streak_sets_streak_as_one_for_irregular_activity(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)
        self.add_activity(habit, update_date=SummaryTests.two_days_ago)
        self.add_activity(habit, update_date=datetime.today())

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(1)

    def test_update_streak_sets_streak_as_zero_for_irregular_activity(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)
        self.add_activity(habit, update_date=SummaryTests.two_days_ago)
        # There is no activity yesterday and today

        summary = models.Summary.update_streak(habit)

        expect(summary.streak).to.equal(0)

    def test_get_streak_should_add_days_for_zero_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=0)

        streak = habit.summary.get().get_streak()

        expect(streak).to.equal("0 days")

    def test_get_streak_should_add_days_for_plural_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=20)

        streak = habit.summary.get().get_streak()

        expect(streak).to.equal("20 days")

    def test_get_streak_should_add_days_for_one_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=1)

        streak = habit.summary.get().get_streak()

        expect(streak).to.equal("1 day")
