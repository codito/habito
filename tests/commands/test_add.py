# -*- coding: utf-8 -*-
"""Tests for add command."""
import habito
import habito.commands
from habito import models
from tests.commands import HabitoCommandTestCase


class HabitoAddTestCase(HabitoCommandTestCase):
    def test_habito_add_should_add_a_habit(self):
        result = self._run_command(habito.commands.add, ["dummy habit", "10.01"])

        assert result.exit_code == 0
        assert models.Habit.get().name == "dummy habit"
        assert models.Summary.get().streak == 0
