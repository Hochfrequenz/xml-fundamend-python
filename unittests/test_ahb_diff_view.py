from datetime import date
from pathlib import Path
from typing import Generator

import pytest
import sqlalchemy
from efoli import EdifactFormatVersion
from sqlmodel import Session, create_engine, select, text
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import create_ahbtabellen_view, create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.ahb_diff_view import AhbDiffLine, DiffStatus, create_ahb_diff_view
from fundamend.sqlmodels.expression_view import create_and_fill_ahb_expression_table

from .conftest import is_private_submodule_checked_out

private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"


@pytest.fixture(scope="module")
def diff_view_session() -> Generator[Session, None, None]:
    """
    Module-scoped fixture that creates a database with the diff view.
    This is expensive to create, so we reuse it across tests in this module.
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


@pytest.mark.snapshot
def test_ahb_diff_view_various_pruefis(snapshot: SnapshotAssertion) -> None:
    """
    Test the diff view by comparing between FV2410 and FV2504.
    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    ahb_paths = [
        (p, date(2024, 10, 1), date(2025, 6, 6)) for p in (private_submodule_root / "FV2410").rglob("**/*AHB*.xml")
    ] + [(p, date(2025, 6, 6), None) for p in (private_submodule_root / "FV2504").rglob("**/*AHB*.xml")]

    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=False)
    assert actual_sqlite_path.exists()
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    results: list[AhbDiffLine] = []
    with Session(bind=engine) as session:
        create_ahbtabellen_view(session)
        create_ahb_diff_view(session)
        for pruefidentifikator in [
            # Existing prüfis
            "55109",
            "29002",
            "44042",
            "31005",
            "27001",
            "13002",
            "19011",
            "15003",
            # New prüfis to test structural changes (added/deleted elements)
            "21000",  # IFTSTA - status messages
            "21001",  # IFTSTA - another status message prüfi
            "33001",  # REMADV - remittance advice
            "37001",  # PARTIN - party information
            "25001",  # UTILTS - utility time series
            "39000",  # ORDCHG - order change (major version difference)
            "13007",  # MSCONS - metered services consumption
            "17001",  # ORDERS - orders
            "31001",  # INVOIC - invoice
            "17101",  # ORDERS - another orders prüfi
        ]:
            # the pruefis chosen are arbitrary. they should just cover some common EdifactFormats.
            stmt = (
                select(AhbDiffLine)
                .where(AhbDiffLine.new_format_version == EdifactFormatVersion.FV2504)
                .where(AhbDiffLine.old_format_version == EdifactFormatVersion.FV2410)
                .where(AhbDiffLine.new_pruefidentifikator == pruefidentifikator)
                .where(AhbDiffLine.old_pruefidentifikator == pruefidentifikator)
                .where(AhbDiffLine.diff_status != "unchanged")
                .order_by(AhbDiffLine.sort_path)
            )
            sub_results = session.exec(stmt).all()
            results.extend(sub_results)
    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    snapshot.assert_match(raw_results)


def test_diff_view_self_comparison_returns_only_unchanged(diff_view_session: Session) -> None:
    """
    Test that comparing a version to itself returns only 'unchanged' entries.
    This verifies the diff logic is correct - nothing should be added/deleted/modified.
    """
    result = diff_view_session.execute(
        text("""
        SELECT diff_status, COUNT(*) as cnt
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2504' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
        GROUP BY diff_status
    """)
    )
    status_counts = {row[0]: row[1] for row in result}

    assert "added" not in status_counts, "Self-comparison should not have 'added' entries"
    assert "deleted" not in status_counts, "Self-comparison should not have 'deleted' entries"
    assert "modified" not in status_counts, "Self-comparison should not have 'modified' entries"
    assert "unchanged" in status_counts, "Self-comparison should have 'unchanged' entries"
    assert status_counts["unchanged"] > 0, "Self-comparison should have at least one unchanged entry"


def test_diff_view_symmetry_added_deleted(diff_view_session: Session) -> None:
    """
    Test that diff is symmetric: added in forward direction = deleted in reverse direction.
    This is a fundamental property that must hold for the diff to be correct.
    """
    # Forward direction: FV2410 -> FV2504
    result_fwd = diff_view_session.execute(
        text("""
        SELECT diff_status, COUNT(*) as cnt
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
        GROUP BY diff_status
    """)
    )
    fwd = {row[0]: row[1] for row in result_fwd}

    # Reverse direction: FV2504 -> FV2410
    result_rev = diff_view_session.execute(
        text("""
        SELECT diff_status, COUNT(*) as cnt
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2504' AND new_format_version = 'FV2410'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
        GROUP BY diff_status
    """)
    )
    rev = {row[0]: row[1] for row in result_rev}

    # Added in forward should equal deleted in reverse
    assert fwd.get("added", 0) == rev.get("deleted", 0), "Forward 'added' should equal reverse 'deleted'"
    assert fwd.get("deleted", 0) == rev.get("added", 0), "Forward 'deleted' should equal reverse 'added'"

    # Modified and unchanged should be the same in both directions
    assert fwd.get("modified", 0) == rev.get("modified", 0), "Modified count should be symmetric"
    assert fwd.get("unchanged", 0) == rev.get("unchanged", 0), "Unchanged count should be symmetric"


def test_diff_view_no_duplicate_id_paths(diff_view_session: Session) -> None:
    """
    Test that there are no duplicate id_paths for the same version pair comparison.
    Each id_path should appear exactly once in the diff results.
    """
    result = diff_view_session.execute(
        text("""
        SELECT id_path, COUNT(*) as cnt
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
        GROUP BY id_path
        HAVING COUNT(*) > 1
    """)
    )
    duplicates = list(result)
    assert len(duplicates) == 0, f"Found duplicate id_paths in diff results: {duplicates[:5]}"


def test_diff_view_added_rows_have_null_old_columns(diff_view_session: Session) -> None:
    """
    Test that 'added' rows have NULL values for old_* columns and populated new_* columns.
    This verifies the SQL is correctly setting NULL for the old version.
    """
    result = diff_view_session.execute(
        text("""
        SELECT
            SUM(CASE WHEN old_segment_code IS NOT NULL THEN 1 ELSE 0 END) as old_segment_not_null,
            SUM(CASE WHEN old_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as old_status_not_null,
            SUM(CASE WHEN new_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as new_status_not_null
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
          AND diff_status = 'added'
    """)
    )
    row = list(result)[0]
    assert row[0] == 0, "Added rows should have NULL old_segment_code"
    assert row[1] == 0, "Added rows should have NULL old_line_ahb_status"
    assert row[2] > 0, "Added rows should have non-NULL new_line_ahb_status"


def test_diff_view_deleted_rows_have_null_new_columns(diff_view_session: Session) -> None:
    """
    Test that 'deleted' rows have NULL values for new_* columns and populated old_* columns.
    This verifies the SQL is correctly setting NULL for the new version.
    """
    result = diff_view_session.execute(
        text("""
        SELECT
            SUM(CASE WHEN new_segment_code IS NOT NULL THEN 1 ELSE 0 END) as new_segment_not_null,
            SUM(CASE WHEN new_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as new_status_not_null,
            SUM(CASE WHEN old_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as old_status_not_null
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
          AND diff_status = 'deleted'
    """)
    )
    row = list(result)[0]
    assert row[0] == 0, "Deleted rows should have NULL new_segment_code"
    assert row[1] == 0, "Deleted rows should have NULL new_line_ahb_status"
    assert row[2] > 0, "Deleted rows should have non-NULL old_line_ahb_status"


def test_diff_view_modified_rows_have_actual_differences(diff_view_session: Session) -> None:
    """
    Test that 'modified' rows actually have differences in at least one compared field.
    This verifies the CASE statement logic is correct.
    """
    result = diff_view_session.execute(
        text("""
        SELECT id_path, old_line_ahb_status, new_line_ahb_status,
               old_line_name, new_line_name, old_bedingung, new_bedingung
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
          AND diff_status = 'modified'
    """)
    )
    for row in result:
        id_path, old_status, new_status, old_name, new_name, old_bed, new_bed = row
        # At least one of status, name, or bedingung must be different
        status_diff = (old_status or "") != (new_status or "")
        name_diff = (old_name or "") != (new_name or "")
        bed_diff = (old_bed or "") != (new_bed or "")
        assert status_diff or name_diff or bed_diff, f"Modified row {id_path} has no actual differences"


def test_diff_view_nonexistent_pruefi_returns_empty(diff_view_session: Session) -> None:
    """
    Test that querying a non-existent prüfidentifikator returns empty results.
    """
    result = diff_view_session.execute(
        text("""
        SELECT COUNT(*) FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '99999' AND new_pruefidentifikator = '99999'
    """)
    )
    count = list(result)[0][0]
    assert count == 0, "Non-existent prüfi should return no results"
