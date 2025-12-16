from datetime import date

import pytest
from efoli import EdifactFormatVersion
from sqlmodel import Session, create_engine, select, text
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import create_ahbtabellen_view, create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.ahb_diff_view import AhbDiffLine, create_ahb_diff_view

from .conftest import is_private_submodule_checked_out, private_submodule_root


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


# Comparing inside the same format version (or old>=new) is no longer possible with the v_ahb_diff in version >=v0.32.0.
# We restricted a CTE such that only same prüfi old < new format version comparisons are possible.
# This makes the view less general purpose but way faster, because somehow the WHERE claudes by the client in the end
# haven't been pushed down to the CTE level to reduce the number of entries there.


def test_diff_view_no_duplicate_id_paths(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that there are no duplicate id_paths for the same version pair comparison.
    Each id_path should appear exactly once in the diff results.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text(
            """
        SELECT id_path, COUNT(*) as cnt
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
        GROUP BY id_path
        HAVING COUNT(*) > 1
    """
        )
    )
    duplicates = list(result)
    assert len(duplicates) == 0, f"Found duplicate id_paths in diff results: {duplicates[:5]}"


def test_diff_view_added_rows_have_null_old_columns(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that 'added' rows have NULL values for old_* columns and populated new_* columns.
    This verifies the SQL is correctly setting NULL for the old version.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text(
            """
        SELECT
            SUM(CASE WHEN old_segment_code IS NOT NULL THEN 1 ELSE 0 END) as old_segment_not_null,
            SUM(CASE WHEN old_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as old_status_not_null,
            SUM(CASE WHEN new_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as new_status_not_null
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
          AND diff_status = 'added'
    """
        )
    )
    row = list(result)[0]
    assert row[0] == 0, "Added rows should have NULL old_segment_code"
    assert row[1] == 0, "Added rows should have NULL old_line_ahb_status"
    assert row[2] > 0, "Added rows should have non-NULL new_line_ahb_status"


def test_diff_view_deleted_rows_have_null_new_columns(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that 'deleted' rows have NULL values for new_* columns and populated old_* columns.
    This verifies the SQL is correctly setting NULL for the new version.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text(
            """
        SELECT
            SUM(CASE WHEN new_segment_code IS NOT NULL THEN 1 ELSE 0 END) as new_segment_not_null,
            SUM(CASE WHEN new_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as new_status_not_null,
            SUM(CASE WHEN old_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as old_status_not_null
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
          AND diff_status = 'deleted'
    """
        )
    )
    row = list(result)[0]
    assert row[0] == 0, "Deleted rows should have NULL new_segment_code"
    assert row[1] == 0, "Deleted rows should have NULL new_line_ahb_status"
    assert row[2] > 0, "Deleted rows should have non-NULL old_line_ahb_status"


def test_diff_view_modified_rows_have_actual_differences(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that 'modified' rows actually have differences in at least one compared field.
    This verifies the CASE statement logic is correct.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text(
            """
        SELECT id_path, old_line_ahb_status, new_line_ahb_status,
               old_line_name, new_line_name, old_bedingung, new_bedingung
        FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55109' AND new_pruefidentifikator = '55109'
          AND diff_status = 'modified'
    """
        )
    )
    for row in result:
        id_path, old_status, new_status, old_name, new_name, old_bed, new_bed = row
        # At least one of status, name, or bedingung must be different
        status_diff = (old_status or "") != (new_status or "")
        name_diff = (old_name or "") != (new_name or "")
        bed_diff = (old_bed or "") != (new_bed or "")
        assert status_diff or name_diff or bed_diff, f"Modified row {id_path} has no actual differences"


def test_diff_view_nonexistent_pruefi_returns_empty(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that querying a non-existent prüfidentifikator returns empty results.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text(
            """
        SELECT COUNT(*) FROM v_ahb_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '99999' AND new_pruefidentifikator = '99999'
    """
        )
    )
    count = list(result)[0][0]
    assert count == 0, "Non-existent prüfi should return no results"


@pytest.mark.snapshot
def test_ahb_diff_view_mscons_13009(
    session_fv2510_fv2604_mscons_with_diff_view: Session, snapshot: SnapshotAssertion
) -> None:
    """
    Test the diff view by comparing MSCONS between versions
    """
    stmt = (
        select(AhbDiffLine)
        .where(AhbDiffLine.new_format_version == EdifactFormatVersion.FV2510)
        .where(AhbDiffLine.old_format_version == EdifactFormatVersion.FV2604)
        .where(AhbDiffLine.new_pruefidentifikator == "13009")
        .where(AhbDiffLine.old_pruefidentifikator == "13009")
        .where(AhbDiffLine.diff_status != "unchanged")
        .order_by(AhbDiffLine.sort_path)
    )
    results = session_fv2510_fv2604_mscons_with_diff_view.exec(stmt).all()
    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    snapshot.assert_match(raw_results)
