# -*- coding: utf-8 -*-
"""Tests for delete command."""
import habito
import habito.commands
from tests.commands import HabitoCommandTestCase


class HabitoDeleteTestCase(HabitoCommandTestCase):
    def test_delete_removes_habit_activity(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, [habit.name, "-q 3"])

        delete_result = self._run_command_with_stdin(habito.commands.delete, ["1"], "y")

        msg = (
            "Are you sure you want to delete habit 1: {} (this cannot be"
            " undone!)".format(habit.name)
        )
        assert msg in delete_result.output
        assert (
            "{0}: {1} has been deleted!".format(habit.id, habit.name)
            in delete_result.output
        )
        assert habito.models.Habit.select().count() == 0

    def test_delete_should_not_delete_for_no_confirm(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, [habit.name, "-q 3"])

        delete_result = self._run_command_with_stdin(habito.commands.delete, ["1"], "n")

        msg = (
            "Are you sure you want to delete habit 1: {} (this cannot be"
            " undone!)".format(habit.name)
        )
        assert msg in delete_result.output
        assert habito.models.Habit.select().count() == 1

    def test_non_existing_delete(self):
        delete_result = self._run_command(habito.commands.delete, ["20"])

        assert (
            "The habit you want to remove does not seem to exist!"
            in delete_result.output
        )

    def test_delete_with_keep_logs_marks_habit_inactive(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, [habit.name, "-q 3"])

        delete_result = self._run_command_with_stdin(
            habito.commands.delete, ["1", "--keeplogs"], "y"
        )

        assert delete_result.exit_code == 0
        assert habito.models.Activity.select().count() == 1
        assert (
            habito.models.Habit.select().where(habito.models.Habit.active).count() == 0
        )
