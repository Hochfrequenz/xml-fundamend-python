"""contains the entrypoint for the command line interface"""

import typer
from rich.console import Console

from fundamend.commands import app as commands_app

app = typer.Typer(name="fundamend", help="CLI tool to work with XML files by BDEW", no_args_is_help=True)
err_console = Console(stderr=True)  # https://typer.tiangolo.com/tutorial/printing/#printing-to-standard-error


app.add_typer(commands_app)


def cli() -> None:
    """entry point of the script defined in pyproject.toml"""
    typer.run(app)


if __name__ == "__main__":
    app()
