# -*- coding: utf-8 -*-
"""Habito add command."""
from datetime import datetime

import click
import dateparser
import sys

from habito import models as models

EXAMPLES = """
    Examples:

    \b
    habito add "Write every day" 700 --units words
    habito add "Cycle twice a week" 2 --units rounds --interval 7
    habito add "Wake up before 6am" 6 --units am --minimize
    habito add "Walk to work" 1 --units times
"""


@click.command(epilog=EXAMPLES)
@click.argument("name", nargs=-1)
@click.argument("quantum", type=click.FLOAT)
@click.option("--units", "-u", default="units", help="Units of data.")
@click.option(
    "--interval",
    "-i",
    type=click.INT,
    default=1,
    help="Check-in interval in days. Default: 1 day.",
)
@click.option(
    "--minimize",
    is_flag=True,
    default=False,
    help=(
        "Treat QUANTUM as upper bound. "
        "Any lesser value will be considered successful check-in."
    ),
)
@click.option(
    "--start-date",
    type=click.STRING,
    default="today",
    help="Start date for tracking the habit. Default: today.",
)
def add(name, quantum, units, interval, minimize, start_date):
    """Add a habit NAME with QUANTUM goal."""
    habit_name = " ".join(name)
    track_date = dateparser.parse(start_date)
    if track_date is None:
        click.echo(f"Unable to parse start date: {start_date}.")
        sys.exit(1)

    models.Habit.add(
        name=habit_name,
        created_date=datetime.now(),
        start_date=track_date,
        quantum=quantum,
        units=units,
        frequency=interval,
        minimize=minimize,
        magica="",
    )

    msg_neg = "<" if minimize else ""
    msg_unit = click.style(f"{msg_neg}{quantum} {units}", fg="green")
    msg_name = click.style(f"{habit_name}", fg="green")
    msg_interval = click.style(f"{interval} days", fg="green")
    click.echo(f"You have commited to {msg_unit} of {msg_name} every {msg_interval}!")
