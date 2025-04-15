from datetime import date
from pathlib import Path

import pytest
from sqlmodel import Session, col, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.expression_view import AhbExpression, create_and_fill_ahb_expression_table

from .conftest import is_private_submodule_checked_out


@pytest.mark.snapshot
def test_create_db_and_expressions_view(snapshot: SnapshotAssertion) -> None:
    ahb_paths = [
        (
            Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml",
            date(2023, 10, 1),
            date(2024, 4, 3),
        )
    ]
    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=True)
    assert actual_sqlite_path.exists()
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_expression_table(session)
        stmt = select(AhbExpression).where(AhbExpression.format == "UTILTS").order_by(AhbExpression.expression)
        results = session.exec(stmt).all()
    raw_results = [r.model_dump(mode="json") for r in results]
    for raw_result in raw_results:
        for guid_column in ["id", "anwendungshandbuch_primary_key"]:  # there's no point to compare those
            if guid_column in raw_result:
                del raw_result[guid_column]
    snapshot.assert_match(raw_results)


@pytest.mark.snapshot
def test_create_expressions_table_from_submodule_with_validity(snapshot: SnapshotAssertion) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    relevant_files = [
        (p, date(2024, 10, 1), date(2025, 6, 6)) for p in (private_submodule_root / "FV2410").rglob("**/*AHB*.xml")
    ] + [(p, date(2025, 6, 6), None) for p in (private_submodule_root / "FV2504").rglob("**/*AHB*.xml")]
    actual_sqlite_path = create_db_and_populate_with_ahb_view(relevant_files, drop_raw_tables=True)
    assert actual_sqlite_path.exists()
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_expression_table(session)
        # just to check we don't run into any constraints or unexpected errors when using _all_ AHBs
        stmt = (
            select(AhbExpression)
            .where(col(AhbExpression.ahbicht_error_message).isnot(None))  # pylint:disable=no-member
            .order_by(AhbExpression.edifact_format_version, AhbExpression.format, AhbExpression.expression)
        )
        # as a by-product of this test we get a snapshot of all expressions that are invalid in all AHBs
        results = session.exec(stmt).all()
    raw_results = [r.model_dump(mode="json") for r in results]
    for raw_result in raw_results:
        for guid_column in ["id", "anwendungshandbuch_primary_key"]:  # there's no point to compare those
            if guid_column in raw_result:
                del raw_result[guid_column]
    snapshot.assert_match(raw_results)
