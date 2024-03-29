# -*- coding: utf-8 -*-
"""Tests for add command."""
from datetime import datetime
import habito
import habito.commands
from habito import models
from tests.commands import HabitoCommandTestCase


class HabitoAddTestCase(HabitoCommandTestCase):
    def test_habito_add_should_add_a_habit(self):
        result = self._run_command(habito.commands.add, ["dummy habit", "10.01"])

        habit = models.Habit.get()
        assert result.exit_code == 0
        assert habit.name == "dummy habit"
        assert habit.quantum == 10.01
        assert habit.units == "units"
        assert habit.frequency == 1
        assert models.Summary.get().streak == 0

    def test_habito_add_with_interval(self):
        result = self._run_command(
            habito.commands.add, ["dummy habit", "10.01", "-u", "words", "-i", 2]
        )

        habit = models.Habit.get()
        assert result.exit_code == 0
        assert habit.name == "dummy habit"
        assert habit.frequency == 2
        assert habit.units == "words"

    def test_habito_add_invert_habit(self):
        result = self._run_command(
            habito.commands.add, ["dummy habit", "10.01", "--minimize"]
        )

        habit = models.Habit.get()
        assert result.exit_code == 0
        assert habit.name == "dummy habit"
        assert habit.minimize is True

    def test_habito_add_start_date(self):
        today = datetime.now().date()
        dates = [("", 1, None), (None, 0, today), ("today", 0, today)]
        for date in dates:
            result = self._run_command(
                habito.commands.add,
                ["dummy habit", "10.01", "--start-date", date[0]],
            )

            assert result.exit_code == date[1]
            if date[1] == 0:
                habit = models.Habit.get()
                assert habit.start_date == date[2]
