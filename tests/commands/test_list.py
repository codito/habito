# -*- coding: utf-8 -*-
"""Tests for list command."""
from datetime import datetime, timedelta
from unittest.mock import patch

import habito
import habito.commands
from tests.commands import HabitoCommandTestCase


class HabitoListCommandTestCase(HabitoCommandTestCase):
    def test_habito_list_default_format_is_table(self):
        habit = self.create_habit()
        self.add_summary(habit)

        result = self._run_command(habito.commands.list, ["-l"])

        assert "id,name," not in result.output

    def test_habito_list_csv_duration(self):
        habit_one = self.create_habit()
        self.add_summary(habit_one)

        result = self._run_command(
            habito.commands.list, ["-l", "-f", "csv", "-d", "13 days"]
        )

        # 1 habit for 13 days = 15 data points incl header and footer
        assert 15 == len(result.output.splitlines())

    def test_habito_list_csv_invalid_from_date(self):
        habit_one = self.create_habit()
        self.add_summary(habit_one)

        result = self._run_command(
            habito.commands.list, ["-l", "-f", "csv", "-d", "13 nights"]
        )

        assert 1 == result.exit_code

    def test_habito_list_csv_headers_and_data(self):
        habit_one = self.create_habit()
        habit_two = self.create_habit(name="HabitTwo")
        self.add_summary(habit_one)
        self.add_summary(habit_two)
        three_days_back = (datetime.now() - timedelta(days=3)).date()
        self._run_command(habito.commands.checkin, ["One", "-q 3.0"])
        self._run_command(habito.commands.checkin, ["One", "-q 2.0"])

        result = self._run_command(habito.commands.list, ["-l", "-f", "csv"])

        # 2 habits for 7 days = 16 data points incl header and footer
        assert "id,name,goal,units,date,activity" in result.output
        assert (
            f"1,HabitOne,0.0,dummy_units,{datetime.now().date()},5.0" in result.output
        )
        assert f"1,HabitOne,0.0,dummy_units,{three_days_back},0.0" in result.output
        assert f"2,HabitTwo,0.0,dummy_units,{three_days_back},0.0" in result.output
        assert 16 == len(result.output.splitlines())

    def test_habito_list_lists_off_track_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, ["Habit", "-q -9.1"])

        result = self._run_command(habito.commands.list, ["-l"])

        # Habit is off track with quanta <= goal. Verify 'x'
        assert habit.name in result.output
        assert "-9.1" in result.output

    def test_habito_list_lists_on_track_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, ["Habit", "-q 9.1"])

        result = self._run_command(habito.commands.list, ["-l"])

        # Habit is on track with quanta >= goal. Verify 'tick'
        assert habit.name in result.output
        assert "9.1" in result.output

    def test_habito_list_skips_inactive_habits(self):
        habit = self.create_habit()
        self.add_summary(habit)
        self._run_command(habito.commands.checkin, ["Habit", "-q 9.1"])
        habit.active = False
        habit.save()

        result = self._run_command(habito.commands.list, ["-l"])

        # Habit is on track with quanta >= goal. Verify 'tick'
        assert habit.name not in result.output
        assert "9.1" not in result.output

    def test_habito_list_should_show_streak(self):
        habit = self.create_habit()
        self.add_summary(habit, streak=10)

        result = self._run_command(habito.commands.list)

        assert "10 days" in result.output

    @patch("shutil.get_terminal_size")
    def test_habito_list_table_adapts_to_terminal_width(self, term_mock):
        for terminal_width in range(0, 101, 5):
            term_mock.return_value = (terminal_width, 80)
            nr_of_dates = terminal_width // 10 - 4
            result = self._run_command(habito.commands.list, ["-l"])
            if nr_of_dates < 1:
                assert "terminal window is too small" in result.output
                assert result.exit_code == 1
            else:
                assert result.exit_code == 0
                for i in range(nr_of_dates):
                    date_string = "{dt.month}/{dt.day}".format(
                        dt=(datetime.now() - timedelta(days=i))
                    )
                    assert date_string in result.output
