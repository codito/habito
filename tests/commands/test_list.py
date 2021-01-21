# -*- coding: utf-8 -*-
"""Tests for list command."""
from datetime import datetime, timedelta
from unittest.mock import patch

import habito
import habito.commands
from tests.commands import HabitoCommandTestCase


class HabitoListCommandTestCase(HabitoCommandTestCase):
    def test_habito_list_lists_off_track_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, ["Habit", "-q -9.1"])

        result = self._run_command(habito.commands.list, ["-l"])

        # Habit is off track with quanta <= goal. Verify 'x'
        assert habit.name in result.output
        assert u"-9.1" in result.output

    def test_habito_list_lists_on_track_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, ["Habit", "-q 9.1"])

        result = self._run_command(habito.commands.list, ["-l"])

        # Habit is on track with quanta >= goal. Verify 'tick'
        assert habit.name in result.output
        assert u"9.1" in result.output

    def test_habito_list_skips_inactive_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, ["Habit", "-q 9.1"])
        habit.active = False
        habit.save()

        result = self._run_command(habito.commands.list, ["-l"])

        # Habit is on track with quanta >= goal. Verify 'tick'
        assert habit.name not in result.output
        assert u"9.1" not in result.output

    def test_habito_list_should_show_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)

        result = self._run_command(habito.commands.list)

        assert "10 days" in result.output

    @patch("click.get_terminal_size")
    def test_habito_list_table_adapts_to_terminal_width(self, term_mock):
        for terminal_width in range(0, 101, 5):
            term_mock.return_value = (terminal_width, 80)
            nr_of_dates = terminal_width//10 - 4
            result = self._run_command(habito.commands.list, ["-l"])
            if nr_of_dates < 1:
                assert "terminal window is too small" in result.output
                assert result.exit_code == 1
            else:
                assert result.exit_code == 0
                for i in range(nr_of_dates):
                    date_string = "{dt.month}/{dt.day}".format(dt=(datetime.now() - timedelta(days=i)))
                    assert date_string in result.output
