from datetime import date
from pathlib import Path

import pytest
from sqlmodel import Session, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend.sqlmodels import create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.expression_view import AhbExpression, create_and_fill_ahb_expression_table


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
        stmt = (
            select(AhbExpression).where(AhbExpression.pruefidentifikator == "25001").order_by(AhbExpression.expression)
        )
        results = session.exec(stmt).all()
    raw_results = [r.model_dump(mode="json") for r in results]
    for raw_result in raw_results:
        for guid_column in ["id"]:  # there's no point to compare those
            if guid_column in raw_result:
                del raw_result[guid_column]
    snapshot.assert_match(raw_results)
