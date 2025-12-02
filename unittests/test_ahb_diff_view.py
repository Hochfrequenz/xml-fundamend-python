from datetime import date
from pathlib import Path

import pytest
from efoli import EdifactFormatVersion
from sqlmodel import Session, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.ahb_diff_view import AhbDiffLine, create_ahb_diff_view

from .conftest import is_private_submodule_checked_out

private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"


@pytest.mark.snapshot
def test_ahb_diff_view_55001(snapshot: SnapshotAssertion) -> None:
    """
    Test the diff view by comparing Prüfidentifikator 55001 between FV2410 and FV2504.
    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    ahb_paths = [
        (p, date(2024, 10, 1), date(2025, 6, 6)) for p in (private_submodule_root / "FV2410").rglob("**/*AHB*.xml")
    ] + [(p, date(2025, 6, 6), None) for p in (private_submodule_root / "FV2504").rglob("**/*AHB*.xml")]

    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=False)
    assert actual_sqlite_path.exists()
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        create_ahb_diff_view(session)
        # Query the diff view for changes between FV2410 and FV2504
        stmt = (
            select(AhbDiffLine)
            .where(AhbDiffLine.format_version_a == EdifactFormatVersion.FV2504)
            .where(AhbDiffLine.format_version_b == EdifactFormatVersion.FV2410)
            .where(AhbDiffLine.pruefidentifikator_a == "55001")
            .where(AhbDiffLine.pruefidentifikator_b == "55001")
            .where(AhbDiffLine.diff_status != "unchanged")
            .order_by(AhbDiffLine.sort_path)
        )
        results = session.exec(stmt).all()

    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    # Remove columns that are not relevant for comparison
    for raw_result in raw_results:
        for column in ["format_version_a", "format_version_b", "pruefidentifikator_a", "pruefidentifikator_b"]:
            if column in raw_result:
                del raw_result[column]

    snapshot.assert_match(raw_results)
