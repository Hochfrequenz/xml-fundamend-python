import pytest
from efoli import EdifactFormatVersion
from sqlmodel import Session, select, text
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels.ahb_pruefi_diff_view import AhbPruefiDiffLine


@pytest.mark.snapshot
def test_ahb_pruefi_diff_view_various_pruefi_pairs(
    session_fv2410_fv2504_with_diff_view: Session, snapshot: SnapshotAssertion
) -> None:
    """
    Test the pruefi diff view by comparing different Pruefidentifikatoren within FV2410.
    """
    results: list[AhbPruefiDiffLine] = []
    for pruefi_old, pruefi_new in [
        ("55001", "55002"),  # UTILMD Strom
        ("17001", "17101"),  # ORDERS
    ]:
        stmt = (
            select(AhbPruefiDiffLine)
            .where(AhbPruefiDiffLine.old_format_version == EdifactFormatVersion.FV2410)
            .where(AhbPruefiDiffLine.new_format_version == EdifactFormatVersion.FV2410)
            .where(AhbPruefiDiffLine.old_pruefidentifikator == pruefi_old)
            .where(AhbPruefiDiffLine.new_pruefidentifikator == pruefi_new)
            .where(AhbPruefiDiffLine.diff_status != "unchanged")
            .order_by(AhbPruefiDiffLine.sort_path)
        )
        sub_results = session_fv2410_fv2504_with_diff_view.exec(stmt).all()
        results.extend(sub_results)
    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    snapshot.assert_match(raw_results)


# Comparing across format versions (or old pruefi >= new pruefi) is not possible with v_ahb_pruefi_diff.
# We restricted the version_pairs CTE to same-format-version, old pruefi < new pruefi comparisons only,
# analogous to the restriction on v_ahb_formatversion_diff (see test_ahb_formatversion_diff_view.py),
# so that the WHERE filters the caller supplies keep the cross-product small and the view fast.


def test_pruefi_diff_view_no_duplicate_id_paths(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that there are no duplicate id_paths for the same pruefi pair comparison.
    Each id_path should appear exactly once in the diff results.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text("""
        SELECT id_path, COUNT(*) as cnt
        FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2410'
          AND old_pruefidentifikator = '55001' AND new_pruefidentifikator = '55002'
        GROUP BY id_path
        HAVING COUNT(*) > 1
    """)
    )
    duplicates = list(result)
    assert len(duplicates) == 0, f"Found duplicate id_paths in diff results: {duplicates[:5]}"


def test_pruefi_diff_view_added_rows_have_null_old_columns(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that 'added' rows have NULL values for old_* columns and populated new_* columns.
    This verifies the SQL is correctly setting NULL for the old pruefidentifikator.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text("""
        SELECT
            SUM(CASE WHEN old_segment_code IS NOT NULL THEN 1 ELSE 0 END) as old_segment_not_null,
            SUM(CASE WHEN old_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as old_status_not_null,
            SUM(CASE WHEN new_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as new_status_not_null
        FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2410'
          AND old_pruefidentifikator = '55001' AND new_pruefidentifikator = '55002'
          AND diff_status = 'added'
    """)
    )
    row = next(iter(result))
    assert row[0] == 0, "Added rows should have NULL old_segment_code"
    assert row[1] == 0, "Added rows should have NULL old_line_ahb_status"
    assert row[2] > 0, "Added rows should have non-NULL new_line_ahb_status"


def test_pruefi_diff_view_deleted_rows_have_null_new_columns(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that 'deleted' rows have NULL values for new_* columns and populated old_* columns.
    This verifies the SQL is correctly setting NULL for the new pruefidentifikator.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text("""
        SELECT
            SUM(CASE WHEN new_segment_code IS NOT NULL THEN 1 ELSE 0 END) as new_segment_not_null,
            SUM(CASE WHEN new_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as new_status_not_null,
            SUM(CASE WHEN old_line_ahb_status IS NOT NULL THEN 1 ELSE 0 END) as old_status_not_null
        FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2410'
          AND old_pruefidentifikator = '55001' AND new_pruefidentifikator = '55002'
          AND diff_status = 'deleted'
    """)
    )
    row = next(iter(result))
    assert row[0] == 0, "Deleted rows should have NULL new_segment_code"
    assert row[1] == 0, "Deleted rows should have NULL new_line_ahb_status"
    assert row[2] > 0, "Deleted rows should have non-NULL old_line_ahb_status"


def test_pruefi_diff_view_modified_rows_have_actual_differences(
    session_fv2410_fv2504_with_diff_view: Session,
) -> None:
    """
    Test that 'modified' rows actually have differences in at least one compared field.
    This verifies the CASE statement logic is correct.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text("""
        SELECT id_path, old_line_ahb_status, new_line_ahb_status,
               old_line_name, new_line_name, old_bedingung, new_bedingung
        FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2410'
          AND old_pruefidentifikator = '55001' AND new_pruefidentifikator = '55002'
          AND diff_status = 'modified'
    """)
    )
    rows = list(result)
    assert len(rows) > 0, "Expected at least one modified row for this pruefi pair"
    for row in rows:
        id_path, old_status, new_status, old_name, new_name, old_bed, new_bed = row
        # At least one of status, name, or bedingung must be different
        status_diff = (old_status or "") != (new_status or "")
        name_diff = (old_name or "") != (new_name or "")
        bed_diff = (old_bed or "") != (new_bed or "")
        assert status_diff or name_diff or bed_diff, f"Modified row {id_path} has no actual differences"


def test_pruefi_diff_view_nonexistent_pruefi_returns_empty(session_fv2410_fv2504_with_diff_view: Session) -> None:
    """
    Test that querying a non-existent pruefidentifikator returns empty results.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text("""
        SELECT COUNT(*) FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2410'
          AND old_pruefidentifikator = '99999' AND new_pruefidentifikator = '55002'
    """)
    )
    count = next(iter(result))[0]
    assert count == 0, "Non-existent pruefi should return no results"


def test_pruefi_diff_view_different_format_versions_returns_empty(
    session_fv2410_fv2504_with_diff_view: Session,
) -> None:
    """
    Test that comparing pruefidentifikatoren across two different format versions returns no results,
    since v_ahb_pruefi_diff is restricted to same-format-version pairs only.
    """
    result = session_fv2410_fv2504_with_diff_view.execute(
        text("""
        SELECT COUNT(*) FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2410' AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55001' AND new_pruefidentifikator = '55002'
    """)
    )
    count = next(iter(result))[0]
    assert count == 0, "Comparing across format versions should return no results"
