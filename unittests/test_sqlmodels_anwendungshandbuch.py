"""
we try to fill a database using kohlrahbi[sqlmodels] and the data from the machine-readable AHB submodule
"""

from datetime import date
from pathlib import Path
from typing import Generator

import pytest
from efoli import EdifactFormatVersion
from pydantic import RootModel
from sqlalchemy import func, text
from sqlmodel import Session, SQLModel, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend import AhbReader
from fundamend.models.anwendungshandbuch import Anwendungshandbuch as PydanticAnwendunghandbuch
from fundamend.models.kommunikationsrichtung import Kommunikationsrichtung
from fundamend.sqlmodels import AhbHierarchyMaterialized
from fundamend.sqlmodels import Anwendungshandbuch as SqlAnwendungshandbuch
from fundamend.sqlmodels import create_ahb_view, create_db_and_populate_with_ahb_view

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


_Kommunikationsrichtungen = RootModel[list[Kommunikationsrichtung]]


def test_sqlmodels_all_anwendungshandbuch_with_ahb_view(sqlite_session: Session) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    for ahb_file_path in private_submodule_root.rglob("**/*AHB*.xml"):
        ahb = AhbReader(ahb_file_path).read()
        sql_ahb = SqlAnwendungshandbuch.from_model(ahb)
        for awf, sql_awf in zip(
            (x for x in ahb.anwendungsfaelle if not x.is_outdated),
            # this is because outdated AWF are not included in the SQL model;
            # see the SqlAnwendungshandbuch.from_model implementation.
            sorted(sql_ahb.anwendungsfaelle, key=lambda _awf: _awf.position or 0),
        ):
            # this is for https://github.com/Hochfrequenz/xml-fundamend-python/issues/173
            if awf.kommunikationsrichtungen is not None and any(awf.kommunikationsrichtungen):
                sql_kommunikationsrichtungen = _Kommunikationsrichtungen.model_validate(
                    sql_awf.kommunikationsrichtungen
                ).root
                assert sql_kommunikationsrichtungen == awf.kommunikationsrichtungen
            else:
                assert sql_awf.kommunikationsrichtungen is None or not any(sql_awf.kommunikationsrichtungen)
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
            "anwendungshandbuch_primary_key",
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


def test_create_sqlite_from_submodule_with_validity() -> None:
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
        stmt = (
            select(AhbHierarchyMaterialized)
            .where(AhbHierarchyMaterialized.pruefidentifikator == "25001")
            .where(AhbHierarchyMaterialized.edifact_format_version == EdifactFormatVersion.FV2504)
            .order_by(AhbHierarchyMaterialized.sort_path)
        )
        results = session.exec(stmt).all()
    assert any(results)
    assert all(x.gueltig_von is not None for x in results)
    assert all(x.kommunikationsrichtungen is not None for x in results)
    assert all(x.beschreibung is not None for x in results)


def _check_uniqueness_of_id_paths(sqlite_path: Path) -> None:
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with Session(bind=engine) as session:
        stmt = (
            select(
                AhbHierarchyMaterialized.id_path,
                AhbHierarchyMaterialized.pruefidentifikator,
                AhbHierarchyMaterialized.edifact_format_version,
                func.count().label("cnt"),  # pylint:disable=not-callable
            )
            .group_by(
                AhbHierarchyMaterialized.id_path,
                AhbHierarchyMaterialized.pruefidentifikator,
                func.coalesce(AhbHierarchyMaterialized.edifact_format_version, ""),
            )
            .having(func.count() > 1)  # pylint:disable=not-callable
            .order_by(func.count().desc())  # pylint:disable=not-callable
        )
        duplicates = session.exec(stmt).all()

    assert not any(duplicates), f"Found duplicate id_paths per pruefidentifikator: {duplicates}"


def test_id_path_uniqueness_per_pruefidentifikator_utilts() -> None:
    """
    Verify that id_path is unique per combination of Prüfidentifikator AND EDIFACT format version.
    This test checks if the id_path construction properly distinguishes between elements
    that appear multiple times in the same AHB, ensuring uniqueness per (pruefidentifikator, edifact_format_version)
    tuple.
    This test is pretty fast because it uses just a single AHB.
    """

    ahb_paths = [Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"]
    actual_sqlite_path = create_db_and_populate_with_ahb_view(ahb_files=ahb_paths, drop_raw_tables=False)
    _check_uniqueness_of_id_paths(actual_sqlite_path)


def _check_id_paths_use_qualifiers_not_sort_path(sqlite_path: Path) -> None:
    """Verify that id_paths use semantic qualifiers (+) instead of positional sort_path (@)."""
    engine = create_engine(f"sqlite:///{sqlite_path}")
    with Session(bind=engine) as session:
        # No id_path should contain the old @sort_path pattern
        at_count = session.execute(
            text("SELECT COUNT(*) FROM ahb_hierarchy_materialized WHERE id_path LIKE '%@%'")
        ).scalar()
        assert at_count == 0, f"Found {at_count} id_paths with old @sort_path pattern"

        # At least some id_paths should contain qualifier (+) pattern
        plus_count = session.execute(
            text("SELECT COUNT(*) FROM ahb_hierarchy_materialized WHERE id_path LIKE '%+%'")
        ).scalar()
        assert plus_count is not None and plus_count > 0, "Expected some id_paths with semantic qualifiers (+)"


@pytest.mark.parametrize(
    "format_version,gueltig_von,gueltig_bis",
    [
        # parametrizing doesn't affect the result as the different ABHs/AWFs won't share the same format version anyway.
        pytest.param("FV2410", date(2024, 10, 1), date(2025, 6, 6), id="FV2410"),
        pytest.param("FV2504", date(2025, 6, 6), date(2025, 10, 1), id="FV2504"),
        pytest.param("FV2510", date(2025, 10, 1), date(2026, 4, 1), id="FV2510"),
        pytest.param("FV2604", date(2026, 4, 1), None, id="FV2604"),
    ],
)
def test_sqlmodels_all_id_path_uniqueness(format_version: str, gueltig_von: date, gueltig_bis: date | None) -> None:
    """this test is pretty slow because it checks against all AHBs"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    format_version_path = private_submodule_root / format_version
    if not format_version_path.exists():
        pytest.skip(f"Format version {format_version} not found in submodule")
    relevant_files = [(p, gueltig_von, gueltig_bis) for p in format_version_path.rglob("**/*AHB*.xml")]
    actual_sqlite_path = create_db_and_populate_with_ahb_view(relevant_files, drop_raw_tables=False)
    _check_uniqueness_of_id_paths(actual_sqlite_path)


@pytest.mark.parametrize(
    "message_type",
    [
        pytest.param("IFTSTA", id="IFTSTA-flat-SG-paths"),
        pytest.param("PARTIN", id="PARTIN-repeated-FII-D_3192"),
        pytest.param("MSCONS", id="MSCONS-repeated-segment-groups"),
        pytest.param("PRICAT", id="PRICAT-repeated-IMD"),
        pytest.param("UTILMD", id="UTILMD-inserted-segments"),
    ],
)
def test_id_path_uniqueness_per_message_type(message_type: str) -> None:
    """
    Test id_path uniqueness for specific message types known to have structural duplicates.
    These are regression tests for issues #256, #258, #259:
    - IFTSTA: flat segment group naming, duplicate STS segments (#258)
    - PARTIN: repeated FII/D_3192 "Name des Kontoinhabers" (#259)
    - MSCONS: repeated segment groups "Referenzangaben" (#259)
    - PRICAT: repeated IMD segments (#259)
    - UTILMD: segment insertions between versions (#256)
    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    fv2510_path = private_submodule_root / "FV2510"
    if not fv2510_path.exists():
        pytest.skip("FV2510 not found in submodule")
    relevant_files = [
        (p, date(2025, 10, 1), date(2026, 4, 1)) for p in fv2510_path.rglob(f"**/{message_type}_AHB*.xml")
    ]
    if not relevant_files:
        pytest.skip(f"No AHB files found for {message_type}")
    actual_sqlite_path = create_db_and_populate_with_ahb_view(relevant_files, drop_raw_tables=False)
    _check_uniqueness_of_id_paths(actual_sqlite_path)
    _check_id_paths_use_qualifiers_not_sort_path(actual_sqlite_path)


def test_id_path_stable_across_versions_utilmd() -> None:
    """
    Regression test for #256: verify that id_paths are stable when comparing UTILMD across format versions.
    When a segment is inserted in a new version, id_paths of unchanged elements should not shift.
    """
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    fv2510_path = private_submodule_root / "FV2510"
    fv2604_path = private_submodule_root / "FV2604"
    if not fv2510_path.exists() or not fv2604_path.exists():
        pytest.skip("FV2510 or FV2604 not found in submodule")
    relevant_files = [
        (p, date(2025, 10, 1), date(2026, 4, 1)) for p in fv2510_path.rglob("**/UTILMD_AHB*Strom*.xml")
    ] + [(p, date(2026, 4, 1), None) for p in fv2604_path.rglob("**/UTILMD_AHB*Strom*.xml")]
    if not relevant_files:
        pytest.skip("No UTILMD Strom AHB files found")
    actual_sqlite_path = create_db_and_populate_with_ahb_view(relevant_files, drop_raw_tables=False)
    _check_uniqueness_of_id_paths(actual_sqlite_path)

    # Verify cross-version id_path overlap: most id_paths from FV2510 should also exist in FV2604
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        # Count how many id_paths are shared between versions for UTILMD/44001
        shared_count = session.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT id_path FROM ahb_hierarchy_materialized
                    WHERE edifact_format_version = 'FV2510' AND pruefidentifikator = '44001'
                    INTERSECT
                    SELECT id_path FROM ahb_hierarchy_materialized
                    WHERE edifact_format_version = 'FV2604' AND pruefidentifikator = '44001'
                )
            """)).scalar()
        old_count = session.execute(text("""
                SELECT COUNT(*) FROM ahb_hierarchy_materialized
                WHERE edifact_format_version = 'FV2510' AND pruefidentifikator = '44001'
            """)).scalar()
        assert old_count is not None and old_count > 0, "Expected UTILMD/44001 rows in FV2510"
        assert shared_count is not None
        overlap_ratio = shared_count / old_count
        # With semantic id_paths, the vast majority should match (>90%)
        # With the old @sort_path approach, this ratio was much lower due to positional shifts
        assert overlap_ratio > 0.9, (
            f"Only {shared_count}/{old_count} ({overlap_ratio:.0%}) id_paths shared between "
            f"FV2510 and FV2604 for UTILMD/44001. Semantic id_paths should be stable across versions."
        )
