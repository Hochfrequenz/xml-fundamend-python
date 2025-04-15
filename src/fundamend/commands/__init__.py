"""
Contains the commands for the CLI.
"""

import typer

from fundamend.commands.xml2json import app as xml2json_app

app = typer.Typer()

app.add_typer(xml2json_app)
