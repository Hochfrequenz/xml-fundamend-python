"""contains the entrypoint for the command line interface"""

from fundamend.commands import app


def main():
    """entry point of the script defined in pyproject.toml"""
    app()


if __name__ == "__main__":
    app()
