# -*- coding: utf-8 -*-
"""Commands for Habito."""
import os
import click

from habito import models
from .add import add
from .checkin import checkin
from .delete import delete
from .edit import edit
from .list import list

database_name = os.path.join(click.get_app_dir("habito"), "habito.db")


@click.group()
def cli():
    """Habito - a simple command line habit tracker."""
    if not os.path.exists(click.get_app_dir("habito")):
        os.mkdir(click.get_app_dir("habito"))
    models.setup(database_name)


cli.add_command(add)
cli.add_command(checkin)
cli.add_command(delete)
cli.add_command(edit)
cli.add_command(list)
