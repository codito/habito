# -*- coding: utf-8 -*-
"""Habito edit command."""
import click

from habito import models


EXAMPLES = """
    Use `list` command to retrieve the habit ID.

    Examples:

    \b
    habito edit 2 --name "Writing"  # Only update habit name
    habito edit 4 --name "Cycle 10 miles" --quantum 10
"""


@click.command(epilog=EXAMPLES)
@click.argument("id", type=click.INT)
@click.option("--name", "-n", help="The new name (leave empty to keep unchanged).")
@click.option(
    "--quantum",
    "-q",
    type=click.FLOAT,
    help="The new quantum (leave empty to keep unchanged).",
)
def edit(id, name, quantum):
    """Edit a habit ID."""
    try:
        habit = models.Habit.get(models.Habit.id == id)
    except models.Habit.DoesNotExist:
        click.echo(
            (
                "The habit you're trying to edit does not exist!"
                "Please use `habito list` to check the id."
            )
        )
        raise SystemExit(1)
    habit.name = name.strip() if name else habit.name
    habit.quantum = quantum or habit.quantum
    habit.save()

    msg_id = click.style(str(habit.id), fg="green")
    msg_name = click.style(habit.name, fg="green")
    msg_quantum = click.style(str(habit.quantum), fg="green")
    click.echo(
        "Habit with id {} has been saved with name: {} and quantum: {}.".format(
            msg_id, msg_name, msg_quantum
        )
    )
