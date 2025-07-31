from datetime import date
from pathlib import Path

import pytest
from sqlmodel import Session, col, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend import AhbReader
from fundamend.models.anwendungshandbuch import Code as PydanticCode
from fundamend.models.anwendungshandbuch import DataElementGroup as PydanticDataElementGroup
from fundamend.models.anwendungshandbuch import Segment as PydanticSegment
from fundamend.models.anwendungshandbuch import SegmentGroup as PydanticSegmentGroup
from fundamend.sqlmodels import AhbHierarchyMaterialized, create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.expression_view import create_and_fill_ahb_expression_table

from .conftest import is_private_submodule_checked_out


# pylint:disable=too-many-locals
@pytest.mark.snapshot
def test_no_missing_lines_in_ahbview_with_duplicate_date_element_id_within_same_segments(
    snapshot: SnapshotAssertion,
) -> None:
    # see: https://github.com/Hochfrequenz/ahb-tabellen/issues/601 for description of the problem
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    relevant_file = private_submodule_root / "FV2504" / "UTILMD_AHB_Strom_2_1_Fehlerkorrektur_20250623.xml"

    # first check that the segments we search for are present in the XML AHB (w/o any SQLite)
    plain_pydantic_anwendungsfaelle = [
        awf for awf in AhbReader(relevant_file).read().anwendungsfaelle if awf.pruefidentifikator == "55001"
    ]
    assert len(plain_pydantic_anwendungsfaelle) == 1
    sg4_groups = [
        sg
        for sg in plain_pydantic_anwendungsfaelle[0].elements
        if isinstance(sg, PydanticSegmentGroup) and sg.id == "SG4"
    ]
    assert len(sg4_groups) == 1
    sts_segments = [seg for seg in sg4_groups[0].elements if isinstance(seg, PydanticSegment) and seg.id == "STS"]
    assert len(sts_segments) == 1
    assert sts_segments[0].number == "00035"
    codes: list[PydanticCode] = []
    for de_group in sts_segments[0].data_elements:
        assert isinstance(de_group, PydanticDataElementGroup)  # could be a plain data element, but in this case isn't
        for data_element in de_group.data_elements:
            for code in data_element.codes:
                codes.append(code)
    e01_codes = [code for code in codes if code.value == "E01"]
    assert len(e01_codes) == 2, "Der Mist ist einfach im XML schon gar nicht vorhanden"

    # now check the sqlite database
    sqlite_path = create_db_and_populate_with_ahb_view([(relevant_file, date(2025, 6, 6), date(2025, 10, 1))])
    assert sqlite_path.exists()
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with Session(bind=engine) as session:
        create_and_fill_ahb_expression_table(session)
        stmt = (
            # https://github.com/Hochfrequenz/ahb-tabellen/issues/601#issuecomment-2904135820
            select(AhbHierarchyMaterialized)
            .where((col(AhbHierarchyMaterialized.pruefidentifikator).is_("55001")))  # pylint:disable=no-member
            .where(col(AhbHierarchyMaterialized.segment_id).is_("STS"))  # pylint:disable=no-member
            .where((col(AhbHierarchyMaterialized.code_value).is_("E01")))  # pylint:disable=no-member
        )
        results = session.exec(stmt).all()
    assert all(x for x in results if x.segment_number == "00035")
    assert len(results) == 2
    raw_results = [r.model_dump(mode="json") for r in results]
    snapshot.assert_match(raw_results)
