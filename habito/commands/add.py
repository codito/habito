# -*- coding: utf-8 -*-
"""Habito add command."""
from datetime import datetime

import click

from habito import models as models


@click.command()
@click.argument("name", nargs=-1)
@click.argument("quantum", type=click.FLOAT)
@click.option("--units", "-u", default="units", help="Units of data.")
def add(name, quantum, units):
    """Add a habit."""
    habit_name = ' '.join(name)
    models.Habit.add(name=habit_name,
                     created_date=datetime.now(),
                     quantum=quantum,
                     units=units,
                     magica="")

    msg_unit = click.style("{0} {1}".format(quantum, units), fg='green')
    msg_name = click.style("{0}".format(habit_name), fg='green')
    click.echo("You have commited to {0} of {1} every day!"
               .format(msg_unit, msg_name))
