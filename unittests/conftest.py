import logging
from collections.abc import Generator, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from fundamend.sqlmodels import create_ahbtabellen_view, create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.ahb_formatversion_diff_view import create_ahb_formatversion_diff_view
from fundamend.sqlmodels.ahb_pruefi_diff_view import create_ahb_pruefi_diff_view
from fundamend.sqlmodels.expression_view import create_and_fill_ahb_expression_table

# Type of the file lists accepted by fundamend's DB builders.
_AhbFile = Path | tuple[Path, date, date | None] | tuple[Path, None, None]

# The ahbicht condition-expression parser (and its lark backend) can emit large volumes of
# DEBUG/INFO log lines while the expensive DB fixtures parse every AHB expression. Formatting
# those lines during pytest's log capture is pure overhead, so pin these loggers to WARNING.
logging.getLogger("ahbicht").setLevel(logging.WARNING)
logging.getLogger("lark").setLevel(logging.WARNING)

private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
example_files_root = Path(__file__).parent / "example_files"


def is_private_submodule_checked_out() -> bool:
    return any(private_submodule_root.iterdir())


def apply_throwaway_sqlite_pragmas(engine: Engine) -> None:
    """
    Register non-durable SQLite PRAGMAs on ``engine`` for throwaway test databases.

    Tests that round-trip many MIGs/AHBs commit repeatedly into a temporary SQLite file; with the
    default ``synchronous=FULL`` every commit fsyncs, which dominated the runtime of the
    "all from submodule" tests. Since these databases are discarded at the end of the test, we can
    safely turn durability off.
    """

    def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA synchronous=OFF")
            cursor.execute("PRAGMA journal_mode=MEMORY")
            cursor.execute("PRAGMA temp_store=MEMORY")
        finally:
            cursor.close()

    event.listen(engine, "connect", _set_sqlite_pragmas)


def _build_ahb_db_with_diff_view(ahb_files: Sequence[_AhbFile]) -> Path:
    """Build a complete AHB database file: raw tables + expression table + ahbtabellen + diff views."""
    db_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_files, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_expression_table(session)
        create_ahbtabellen_view(session)
        create_ahb_formatversion_diff_view(session)
        create_ahb_pruefi_diff_view(session)
        session.commit()
    engine.dispose()
    return db_path


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
    Includes: ahb_hierarchy_materialized, ahb_expressions, v_ahbtabellen,
    v_ahb_formatversion_diff, v_ahb_pruefi_diff.

    This fixture is expensive to create, so it is module-scoped: every test in a module shares one
    build.
    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    ahb_files: Sequence[_AhbFile] = [
        (p, date(2024, 10, 1), date(2025, 6, 6)) for p in (private_submodule_root / "FV2410").rglob("**/*AHB*.xml")
    ] + [(p, date(2025, 6, 6), None) for p in (private_submodule_root / "FV2504").rglob("**/*AHB*.xml")]

    db_path = _build_ahb_db_with_diff_view(ahb_files)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        yield session
    engine.dispose()


@pytest.fixture(scope="module")
def session_fv2510_fv2604_mscons_with_diff_view() -> Generator[Session, None, None]:
    """
    Module-scoped fixture providing a database session with FV510 and FV2604 MSCONS (only) data.
    Includes: ahb_hierarchy_materialized, ahb_expressions, v_ahbtabellen,
    v_ahb_formatversion_diff, v_ahb_pruefi_diff.

    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    ahb_files: Sequence[_AhbFile] = [
        (p, date(2025, 10, 1), date(2026, 4, 1))
        for p in (private_submodule_root / "FV2510").rglob("**/MSCONS_AHB*.xml")
    ] + [(p, date(2026, 4, 1), None) for p in (private_submodule_root / "FV2604").rglob("**/MSCONS_AHB*.xml")]

    db_path = _build_ahb_db_with_diff_view(ahb_files)
    engine = create_engine(f"sqlite:///{db_path}")
    with Session(bind=engine) as session:
        yield session
    engine.dispose()
