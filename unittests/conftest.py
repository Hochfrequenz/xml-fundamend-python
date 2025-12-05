from datetime import date
from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, create_engine

from fundamend.sqlmodels import create_ahbtabellen_view, create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.ahb_diff_view import create_ahb_diff_view
from fundamend.sqlmodels.expression_view import create_and_fill_ahb_expression_table

private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
example_files_root = Path(__file__).parent / "example_files"


def is_private_submodule_checked_out() -> bool:
    return any(private_submodule_root.iterdir())


# =============================================================================
# Shared Database Fixtures with Meaningful Names
# =============================================================================
# These fixtures are module-scoped to speed up tests by reusing expensive DB creation.
# Naming convention: session_<format_versions>_<views_created>
# =============================================================================


@pytest.fixture(scope="module")
def session_fv2410_fv2504_with_diff_view() -> Generator[Session, None, None]:
    """
    Module-scoped fixture providing a database session with FV2410 and FV2504 data.
    Includes: ahb_hierarchy_materialized, ahb_expressions, v_ahbtabellen, v_ahb_diff.

    This fixture is expensive to create (~30s), so it's shared across all tests that need
    to compare FV2410 and FV2504.
    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    ahb_paths = [
        (p, date(2024, 10, 1), date(2025, 6, 6)) for p in (private_submodule_root / "FV2410").rglob("**/*AHB*.xml")
    ] + [(p, date(2025, 6, 6), None) for p in (private_submodule_root / "FV2504").rglob("**/*AHB*.xml")]

    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        create_ahb_diff_view(session)
        yield session
