# -*- coding: utf-8 -*-
"""List all habits."""
import logging
import shutil
from datetime import datetime, timedelta

import click

from habito import models as models

TICK = u"\u25A0"  # tick - 2713, black square - 25A0, 25AA, 25AF
CROSS = u"\u25A1"  # cross - 2717, white square - 25A1, 25AB, 25AE
PARTIAL = u"\u25A0"  # tick - 2713, black square - 25A0, 25AA, 25AF

logger = logging.getLogger("habito")


@click.command()
@click.option("-l", "long_list", is_flag=True, help="Long listing with date and quantum.")
def list(long_list):
    """List all tracked habits."""
    from terminaltables import SingleTable
    from textwrap import wrap

    terminal_width, terminal_height = shutil.get_terminal_size()

    nr_of_dates = terminal_width // 10 - 4
    if nr_of_dates < 1:
        logger.debug("list: Actual terminal width = {0}.".format(shutil.get_terminal_size()[0]))
        logger.debug("list: Observed terminal width = {0}.".format(terminal_width))
        click.echo("Your terminal window is too small. Please make it wider and try again")
        raise SystemExit(1)

    table_title = ["Habit", "Goal", "Streak"]
    minimal = not long_list
    if minimal:
        table_title.append("Activities")
    else:
        for d in range(0, nr_of_dates):
            date_mod = datetime.today() - timedelta(days=d)
            table_title.append("{0}/{1}".format(date_mod.month, date_mod.day))

    table_rows = [table_title]
    for habit_data in models.get_daily_activities(nr_of_dates):
        habit = habit_data[0]
        habit_row = [str(habit.id) + ": " + habit.name, str(habit.quantum)]
        progress = ""
        for daily_data in habit_data[1]:
            column_text = CROSS
            quanta = daily_data[1]

            if quanta is not None:
                column_text = click.style(PARTIAL)
                if quanta >= habit.quantum:
                    column_text = click.style(TICK, fg="green")
            if minimal:
                progress += column_text + " "
            else:
                habit_row.append(quanta)
        if minimal:
            habit_row.append(progress)

        current_streak = habit.summary.get().get_streak()
        habit_row.insert(2, current_streak)
        table_rows.append(habit_row)

    table = SingleTable(table_rows)

    max_col_width = table.column_max_width(0)
    max_col_width = max_col_width if max_col_width > 0 else 20

    for r in table_rows:
        r[0] = '\n'.join(wrap(r[0], max_col_width))

    click.echo(table.table)
