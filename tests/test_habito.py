# -*- coding: utf-8 -*-
"""Tests for Habito module."""

from datetime import datetime, date, timedelta
from unittest import TestCase
from unittest.mock import patch
from click.testing import CliRunner
from sure import expect

from habito import habito, models
from tests import HabitoTestCase


class HabitoTests(HabitoTestCase):
    """Test scenarios for HabitModel commands."""

    # Scenarios
    # Add: uber goal, daily commitment, automatically add weekly checkpoints
    # Statistics: don't break the chain
    # Suggestions: off track, time to increase difficulty, remind the why!

    # flake8: noqa
    def setUp(self):
        self.runner = CliRunner()
        habito.database_name = ":memory:"
        models.setup(habito.database_name)

    def tearDown(self):
        models.db.drop_tables([models.HabitModel, models.ActivityModel, models.Summary],
                              safe=True)

    def test_habito_cli_sets_up_default_commandset(self):
        result = habito.cli

        commands = { 'list': habito.list, 'add': habito.add,
                    'checkin': habito.checkin }

        expect(result.commands).to.equal(commands)

    @patch("habito.habito.click.get_app_dir")
    @patch("habito.habito.mkdir")
    @patch("habito.habito.models.setup")
    def test_habito_cli_sets_up_database(self, models_setup, mkdir, click):
        result = self._run_command(habito.cli, ["add"])

        expect(models_setup.called).to.true

    @patch("habito.habito.click.get_app_dir")
    @patch("habito.habito.mkdir")
    def test_habito_cli_sets_up_app_directory(self, mkdir_mock, click_mock):
        with patch("habito.habito.path.exists") as path_exists:
            path_exists.return_value = False
            result = self._run_command(habito.cli, ["add"])

            expect(click_mock.called).to.true
            expect(mkdir_mock.called).to.true
   
    def test_habito_list_table_adapts_to_terminal_width(self):
        for terminal_width in range(0, 101, 5):
            nr_of_dates = terminal_width//10 - 3 
            habito.TERMINAL_WIDTH = terminal_width 
            result = self._run_command(habito.list)
            if nr_of_dates < 1:
                expect("terminal window is too small").to.be.within(result.output)
                expect(result.exit_code).to.be(1)
            else:
                expect(result.exit_code).to.be(0)
                for i in range(nr_of_dates):
                    date_string = "{dt.month}/{dt.day}".format(dt=(datetime.now() - timedelta(days=i)))
                    expect(date_string).to.be.within(result.output)
        habito.TERMINAL_WIDTH = 80

    def test_habito_list_lists_tracked_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.checkin, ["Habit", "-q -9.1"])

        result = self._run_command(habito.list)
        expect(habit.name).to.be.within(habit.name)
        expect(u"\u2717 (-9.1)").to.be.within(result.output)

    def test_habito_list_should_show_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)

        result = self._run_command(habito.list)

        expect("10 days").to.be.within(result.output)

    def test_habito_add_should_add_a_habit(self):
        result = self._run_command(habito.add,
                                   ["dummy habit", "10.01"])

        expect(models.HabitModel.get().name).to.eql("dummy habit")
        expect(models.Summary.get().streak).to.be(0)

    def test_habito_checkin_should_show_error_if_no_habit_exists(self):
        result = self._run_command(habito.checkin,
                                   ["dummy habit", "-q 9.1"])

        expect(result.exit_code).to.be(0)
        expect(result.output.startswith("No tracked habits match the")).to.true

    def test_habito_checkin_should_show_error_if_multiple_habits_match(self):
        dummy_date = date(1201, 10, 12)
        habit = self.create_habit()
        habit_two = self.create_habit(name="Habit Two",
                                      created_date=dummy_date,
                                      quantum=0,
                                      magica="be awesome!")

        result = self._run_command(habito.checkin,
                                   ["Habit", "-q 9.1"])

        expect(result.exit_code).to.be(0)
        expect(result.output.startswith("More than one tracked habits match the")).to.true

    def test_habito_checkin_should_add_data_for_a_habit(self):
        habit = self.create_habit()
        self.add_summary(habit)
        result_units = "9.1 dummy_units"

        result = self._run_command(habito.checkin,
                                   ["Habit", "-q 9.1"])

        activity_entry = models.ActivityModel\
            .get(models.ActivityModel.for_habit == habit)

        expect(result.output.find(result_units)).to.not_be(-1)
        expect(result.output.find(habit.name)).to.not_be(-1)
        expect(activity_entry.quantum).to.eql(9.1)

    def test_habito_checkin_can_add_multiple_data_points_on_same_day(self):
        habit = self.create_habit()
        self.add_summary(habit)
        result_units_one = "9.1 dummy_units"
        result_units_two = "10.0001 dummy_units"

        self._run_command(habito.checkin, ["Habit", "-q 9.1"])
        result = self._run_command(habito.checkin, ["Habit", "-q 10.0001"])

        activity_entry = models.ActivityModel\
            .select().where(models.ActivityModel.for_habit == habit)

        expect(result.output.find(result_units_two)).to.not_be(-1)
        expect(result.output.find(habit.name)).to.not_be(-1)
        expect(activity_entry.count()).to.be(2)
        expect(activity_entry[0].quantum).to.eql(9.1)
        expect(activity_entry[1].quantum).to.eql(10.0001)

    def test_habito_checkin_asks_user_input_if_quantum_is_not_provided(self):
        habit = self.create_habit()
        self.add_summary(habit)
        result_units_one = "9.1 dummy_units"

        result = self._run_command_with_stdin(habito.checkin, ["Habit"], "9.1")

        expect(result.exit_code).to.be(0)
        expect(result.output.find(result_units_one)).to.not_be(-1)

    def test_habito_checkin_increments_streak_for_a_habit(self):
        habit = self.create_habit()
        self.add_activity(habit, update_date=HabitoTests.one_day_ago)
        self.add_activity(habit, update_date=HabitoTests.two_days_ago)
        self.add_summary(habit, streak=2)

        self._run_command(habito.checkin, ["Habit", "-q 9.1"])

        expect(models.Summary.get().streak).to.equal(3)

    def _run_command(self, command, args=[]):
        return self._run_command_with_stdin(command, args, stdin=None)

    def _run_command_with_stdin(self, command, args, stdin):
        result = self.runner.invoke(command, args=args, input=stdin)

        print(result.output)
        print(result.exc_info)

        return result
