# -*- coding: utf-8 -*-
"""Tests for edit command."""
import habito
import habito.commands
from tests.commands import HabitoCommandTestCase


class HabitoEditTestCase(HabitoCommandTestCase):
    def test_edit(self):
        habit = self.create_habit()
        self.add_summary(habit)

        edit_result = self._run_command(
            habito.commands.edit, [str(habit.id), "-n EHabit"]
        )

        assert edit_result.output == (
            "Habit with id 1 has been saved with" " name: EHabit and quantum: 0.0.\n"
        )
        list_result = self._run_command(habito.commands.list)
        assert "EHabit" in list_result.output
        assert habit.name not in list_result.output

    def test_edit_quantum(self):
        habit = self.create_habit()
        self.add_summary(habit)

        edit_result = self._run_command(habito.commands.edit, [str(habit.id), "-q 3.0"])

        assert edit_result.output == (
            "Habit with id 1 has been saved with" " name: HabitOne and quantum: 3.0.\n"
        )
        list_result = self._run_command(habito.commands.list)
        assert "3.0" in list_result.output
        assert "0.0" not in list_result.output

    def test_non_existing_edit(self):
        edit_result = self._run_command(habito.commands.edit, [str(10), "-n test"])

        assert edit_result.output == "The habit you're trying to edit does not exist!\n"
        assert edit_result.exit_code == 1
