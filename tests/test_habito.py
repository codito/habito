# -*- coding: utf-8 -*-
"""Tests for Habito module."""

from datetime import datetime, date, timedelta
from unittest.mock import patch
from click.testing import CliRunner

import habito
import habito.commands
import habito.commands.list
import habito.models as models
from tests import HabitoTestCase


class HabitoTests(HabitoTestCase):
    """Test scenarios for Habito commands."""

    # Scenarios
    # Add: uber goal, daily commitment, automatically add weekly checkpoints
    # Statistics: don't break the chain
    # Suggestions: off track, time to increase difficulty, remind the why!

    # flake8: noqa
    def setUp(self):
        self.runner = CliRunner()
        habito.commands.database_name = ":memory:"
        models.setup(habito.commands.database_name)

    def tearDown(self):
        models.db.drop_tables(
            [models.Habit, models.Activity, models.Summary], safe=True
        )

    def test_habito_cli_sets_up_default_commandset(self):
        result = habito.commands.cli

        commands = {
            "list": habito.commands.list,
            "add": habito.commands.add,
            "checkin": habito.commands.checkin,
            "edit": habito.commands.edit,
            "delete": habito.commands.delete,
        }

        assert result.commands == commands

    @patch("click.get_app_dir")
    @patch("os.mkdir")
    @patch("habito.models.setup")
    def test_habito_cli_sets_up_database(self, models_setup, mkdir, click):
        result = self._run_command(habito.commands.cli, ["add"])

        assert models_setup.called

    @patch("click.get_app_dir")
    @patch("os.mkdir")
    def test_habito_cli_sets_up_app_directory(self, mkdir_mock, click_mock):
        with patch("os.path.exists") as path_exists:
            path_exists.return_value = False
            result = self._run_command(habito.commands.cli, ["add"])

            assert click_mock.called
            assert mkdir_mock.called

    def _run_command(self, command, args=[]):
        return self._run_command_with_stdin(command, args, stdin=None)

    def _run_command_with_stdin(self, command, args, stdin):
        result = self.runner.invoke(command, args=args, input=stdin)

        print(result.output)
        print(result.exc_info)

        return result
