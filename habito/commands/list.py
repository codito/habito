# -*- coding: utf-8 -*-
"""List all habits."""
import logging
import shutil
import os
from datetime import datetime, timedelta
from typing import Literal, List, Tuple, Union

import click

from habito import models as models

TICK = "\u25A0"  # tick - 2713, black square - 25A0, 25AA, 25AF
CROSS = "\u25A1"  # cross - 2717, white square - 25A1, 25AB, 25AE
PARTIAL = "\u25A0"  # tick - 2713, black square - 25A0, 25AA, 25AF

logger = logging.getLogger("habito")


@click.command()
@click.option(
    "-l", "long_list", is_flag=True, help="Long listing with date and quantum."
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["csv", "table"], case_sensitive=False),
    default="table",
    help="Output format. Default is table.",
)
@click.option(
    "-d",
    "--duration",
    type=click.STRING,
    default="1 week",
    help=(
        "Duration for the report. Default is 1 week. "
        "If format is table, maximum duration is inferred "
        "from the terminal width."
    ),
)
def list(
    long_list: bool,
    format: Union[Literal["csv"], Literal["table"]] = "table",
    duration="1 week",
):
    """List all tracked habits."""
    nr_of_dates = _get_max_duration(format, duration)
    if format == "csv":
        _show_csv(nr_of_dates)
        return

    _show_table(nr_of_dates, long_list)


def _show_csv(nr_of_dates: int):
    """List habits in csv format grouped by day."""
    if nr_of_dates < 1:
        click.echo("Invalid duration. Try `1 week`, `30 days` or `2 months`.")
        raise SystemExit(1)

    data: List[Tuple[int, float, str]] = []
    data.append((0, 0, f"id,name,goal,units,date,activity{os.linesep}"))
    for habit_data in models.get_daily_activities(nr_of_dates):
        habit = habit_data[0]
        for activity in habit_data[1]:
            for_date = datetime.today() - timedelta(days=activity[0])
            data.append(
                (
                    habit.id,
                    for_date.timestamp(),
                    (
                        f"{habit.id},{habit.name},{habit.quantum},{habit.units}"
                        f",{for_date.date()},{activity[1] or 0.0}"
                        f"{os.linesep}"
                    ),
                )
            )
    data.sort(key=lambda t: t[1])
    click.echo_via_pager(map(lambda d: d[2], data))


def _show_table(nr_of_dates: int, long_list: bool):
    """List habits in tabular format grouped by day."""
    from textwrap import wrap
    from terminaltables import SingleTable

    if nr_of_dates < 1:
        click.echo(
            "Your terminal window is too small. Please make it wider and try again"
        )
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
        r[0] = "\n".join(wrap(r[0], max_col_width))

    click.echo(table.table)


def _get_max_duration(format: str, duration: str) -> int:
    if format != "table":
        import dateparser

        from_date = dateparser.parse(duration)
        if from_date is None:
            logger.debug(f"list: Cannot parse from date. Input duration = {duration}.")
            return -1
        days = (datetime.now() - from_date).days
        return days

    # Calculate duration that fits to the terminal width
    terminal_width, _ = shutil.get_terminal_size()

    nr_of_dates = terminal_width // 10 - 4
    if format == "table" and nr_of_dates < 1:
        logger.debug(
            "list: Actual terminal width = {0}.".format(shutil.get_terminal_size()[0])
        )
        logger.debug("list: Observed terminal width = {0}.".format(terminal_width))
    return nr_of_dates
