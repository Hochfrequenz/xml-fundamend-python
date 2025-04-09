"""
we try to fill a database using kohlrahbi[sqlmodels] and the data from the machine-readable AHB submodule
"""

from datetime import date
from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend import AhbReader
from fundamend.models.anwendungshandbuch import Anwendungshandbuch as PydanticAnwendunghandbuch
from fundamend.sqlmodels.ahbview import create_ahb_view, create_db_and_populate_with_ahb_view
from fundamend.sqlmodels.anwendungshandbuch import AhbHierarchyMaterialized
from fundamend.sqlmodels.anwendungshandbuch import Anwendungshandbuch as SqlAnwendungshandbuch

from .conftest import is_private_submodule_checked_out


@pytest.fixture()
def sqlite_session(tmp_path: Path) -> Generator[Session, None, None]:
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(bind=engine) as session:
        yield session
        session.commit()
        session.flush()
    print(f"Wrote all data to {database_path.absolute()}")


def _load_anwendungshandbuch_ahb_to_and_from_db(
    session: Session, pydantic_ahb: PydanticAnwendunghandbuch
) -> PydanticAnwendunghandbuch:
    sql_ahb = SqlAnwendungshandbuch.from_model(pydantic_ahb)
    session.add(sql_ahb)
    session.commit()
    session.refresh(sql_ahb)
    pydantic_ahb_after_roundtrip = sql_ahb.to_model()
    return pydantic_ahb_after_roundtrip


def test_sqlmodels_single_anwendungshandbuch(sqlite_session: Session) -> None:
    ahb = AhbReader(
        Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    ).read()
    roundtrip_abb = _load_anwendungshandbuch_ahb_to_and_from_db(sqlite_session, ahb)
    ahb_json = ahb.model_dump(mode="json")
    roundtrip_json = roundtrip_abb.model_dump(mode="json")
    assert ahb_json == roundtrip_json  # in pycharm the error message is much better when comparing plain python dicts
    assert roundtrip_abb == ahb


def test_sqlmodels_single_anwendungshandbuch_with_ahb_view(sqlite_session: Session) -> None:
    ahb = AhbReader(
        Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    ).read()
    _ = _load_anwendungshandbuch_ahb_to_and_from_db(sqlite_session, ahb)
    create_ahb_view(session=sqlite_session)
    statement = (
        select(AhbHierarchyMaterialized)
        .where(AhbHierarchyMaterialized.pruefidentifikator == "25001")
        .order_by(AhbHierarchyMaterialized.sort_path)
    )
    results = sqlite_session.exec(statement).all()

    # Correct session execution syntax:
    first_row = results[0]
    last_row = results[-1]
    assert first_row.path == "Nachrichten-Kopfsegment"
    assert last_row.path == "Nachrichten-Endesegment > Nachrichten-Referenznummer"


def test_sqlmodels_all_anwendungshandbuch(sqlite_session: Session) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    for ahb_file_path in private_submodule_root.rglob("**/*AHB*.xml"):
        ahb = AhbReader(ahb_file_path).read()
        ahb_is_not_suited_for_equality_comparison = any(x for x in ahb.anwendungsfaelle if x.is_outdated)
        if ahb_is_not_suited_for_equality_comparison:
            continue
        roundtrip_abb = _load_anwendungshandbuch_ahb_to_and_from_db(sqlite_session, ahb)
        assert roundtrip_abb == ahb


def test_sqlmodels_all_anwendungshandbuch_with_ahb_view(sqlite_session: Session) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    for ahb_file_path in private_submodule_root.rglob("**/*AHB*.xml"):
        ahb = AhbReader(ahb_file_path).read()
        sql_ahb = SqlAnwendungshandbuch.from_model(ahb)
        sqlite_session.add(sql_ahb)
    sqlite_session.commit()
    create_ahb_view(session=sqlite_session)


@pytest.mark.snapshot
@pytest.mark.parametrize("drop_raw_tables", [True, False])
def test_create_db_and_populate_with_ahb_view(drop_raw_tables: bool, snapshot: SnapshotAssertion) -> None:
    ahb_paths = [Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"]
    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=drop_raw_tables)
    assert actual_sqlite_path.exists()
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        stmt = (
            select(AhbHierarchyMaterialized)
            .where(AhbHierarchyMaterialized.pruefidentifikator == "25001")
            .order_by(AhbHierarchyMaterialized.sort_path)
        )
        results = session.exec(stmt).all()
    raw_results = [r.model_dump(mode="json") for r in results]
    for raw_result in raw_results:
        for guid_column in [
            "anwendungsfall_pk",
            "current_id",
            "dataelement_id",
            "code_id",
            "id",
            "root_id",
            "dataelementgroup_id",
            "source_id",
            "parent_id",
            "segmentgroup_anwendungsfall_primary_key",
        ]:  # there's no point to compare those
            if guid_column in raw_result:
                del raw_result[guid_column]
    snapshot.assert_match(raw_results)


@pytest.mark.parametrize("drop_raw_tables", [True, False])
def test_create_db_and_populate_with_ahb_view_with_duplicates(drop_raw_tables: bool) -> None:
    ahb_paths = [
        Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1c_Lesefassung_2023_12_12_ZPbXedn.xml",
        Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml",
    ]
    if drop_raw_tables:
        with pytest.raises(ValueError):
            _ = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=drop_raw_tables)
        return
    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=drop_raw_tables)
    assert actual_sqlite_path.exists()
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        stmt = (
            select(AhbHierarchyMaterialized)
            .where(AhbHierarchyMaterialized.pruefidentifikator == "25001")
            .order_by(AhbHierarchyMaterialized.sort_path)
        )
        results = session.exec(stmt).all()
    assert any(results)


def test_create_sqlite_from_submodule() -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    actual_sqlite_path = create_db_and_populate_with_ahb_view(list(private_submodule_root.rglob("**/*AHB*.xml")))
    assert actual_sqlite_path.exists()


_psr = Path(__file__).parent.parent / "xml-migs-and-ahbs"
_relevant_files_fv2504 = [
    # I really tried to derive the from/to dates from the file names, but it's a pain.
    # We know this from the edi-energy-scraper.
    # FV2504 below; FV2404 above
    (
        _psr / "APERAK" / "APERAK_AHB_2_4a_Fehlerkorrektur_2025_02_25_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "COMDIS" / "COMDIS_AHB_1_0f_ausserordentliche_2025_01_31_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "CONTRL" / "CONTRL_AHB_2_4a_Fehlerkorrektur_2024_12_13_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "IFTSTA" / "IFTSTA_AHB_2_0g_Fehlerkorrektur_2025_02_25_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "INSRPT" / "INSRPT_AHB_1_1g_ausserordentliche_2024_07_26_2023_03_23.xml",
        date(
            2023,
            3,
            23,
        ),
        None,
    ),
    (
        _psr / "INVOIC" / "INVOIC_AHB_2_5d_Fehlerkorrektur_2025_01_31_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "MSCONS" / "MSCONS_AHB_3_1f_Fehlerkorrektur_2025_03_20_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "ORDCHG" / "ORDCHG_AHB_1_0a_2024_10_01_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "ORDERS" / "ORDERS_AHB_1_0a_2024_10_01_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "ORDRSP" / "ORDRSP_AHB_1_0a_2024_10_01_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "PARTIN" / "PARTIN_AHB_1_0e_2024_10_01_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "PRICAT" / "PRICAT_AHB_2_0e_2024_06_19_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "QUOTES" / "QUOTES_AHB_1_0_Fehlerkorrektur_2024_12_13_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "REMADV" / "REMADV_AHB_2_5d_Fehlerkorrektur_2025_01_31_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "REQOTE" / "REQOTE_AHB_1_0a_Fehlerkorrektur_2025_02_25_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "UTILMD" / "UTILMD_AHB_Strom_2_1_Fehlerkorrektur_2025_03_20_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
    (
        _psr / "UTILTS" / "UTILTS_AHB_1_0_Fehlerkorrektur_2025_02_18_2025_06_06.xml",
        date(
            2025,
            6,
            6,
        ),
        None,
    ),
]


def test_create_sqlite_from_submodule_with_validity() -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    assert _psr.exists() and _psr.is_dir()
    actual_sqlite_path = create_db_and_populate_with_ahb_view(_relevant_files_fv2504, drop_raw_tables=True)
    assert actual_sqlite_path.exists()
