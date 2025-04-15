"""contains the entrypoint for the command line interface"""

import json
from pathlib import Path

import typer
from pydantic import RootModel
from rich.console import Console
from typing_extensions import Annotated

from fundamend import AhbReader, Anwendungshandbuch, MessageImplementationGuide, MigReader

app = typer.Typer(name="xml2json", help="Convert XML(s) by BDEW to JSON(s)")
err_console = Console(stderr=True)  # https://typer.tiangolo.com/tutorial/printing/#printing-to-standard-error


def cli() -> None:
    """entry point of the script defined in pyproject.toml"""
    typer.run(main)


if __name__ == "__main__":
    app()
