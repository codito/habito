# -*- coding: utf-8 -*-
"""Habito delete command."""
import click

from habito import models as models


@click.command()
@click.argument("id", type=click.INT)
@click.option("--keeplogs", is_flag=True, default=False,
              help="Preserve activity logs for the habit.")
def delete(id, keeplogs):
    """Delete a habit."""
    try:
        habit = models.Habit.get(models.Habit.id == id)
    except models.Habit.DoesNotExist:
        click.echo("The habit you want to remove does not seem to exist!")
        raise SystemExit(1)
    confirm = click.confirm("Are you sure you want to delete habit"
                            " {}: {} (this cannot be undone!)"
                            .format(habit.id, habit.name))
    if confirm:
        click.echo("Habit {}: {} has been deleted!".format(habit.id, habit.name))
        if not keeplogs:
            models.Activity.delete().where(models.Activity.for_habit ==
                                           habit.id).execute()
            models.Summary.delete().where(models.Summary.for_habit ==
                                          habit.id).execute()
            habit.delete_instance()
        else:
            habit.active = False
            habit.save()
    else:
        click.echo("Habit {}: {} has not been deleted!".format(habit.id, habit.name))
