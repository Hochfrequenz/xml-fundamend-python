import typer
from rich.console import Console

app = typer.Typer(name="fundamend", help="CLI tool to work with XML files by BDEW", no_args_is_help=True)
err_console = Console(stderr=True)  # https://typer.tiangolo.com/tutorial/printing/#printing-to-standard-error
