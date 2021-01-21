# -*- coding: utf-8 -*-
"""Base test case for habito commands."""
from datetime import datetime

from click.testing import CliRunner

import habito
import habito.commands
from habito import models
from tests import HabitoTestCase


class HabitoCommandTestCase(HabitoTestCase):
    # flake8: noqa
    def setUp(self):
        self.runner = CliRunner()
        habito.commands.database_name = ":memory:"
        models.setup(habito.commands.database_name)

    def tearDown(self):
        models.db.drop_tables([models.Habit, models.Activity, models.Summary],
                              safe=True)

    def _verify_checkin_date(self, date_str, year, output):
        date = datetime.strptime(date_str, "%m/%d") \
            .replace(year=year).strftime("%a %b %d %Y")
        assert date in output

    def _run_command(self, command, args=[]):
        return self._run_command_with_stdin(command, args, stdin=None)

    def _run_command_with_stdin(self, command, args, stdin):
        result = self.runner.invoke(command, args=args, input=stdin)

        print(result.output)
        print(result.exc_info)

        return result
