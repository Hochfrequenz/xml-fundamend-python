from pathlib import Path

private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"


def is_private_submodule_checked_out() -> bool:
    return any(private_submodule_root.iterdir())
