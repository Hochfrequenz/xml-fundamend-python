"""
Tests for MIG hierarchy and diff views
"""

from datetime import date
from pathlib import Path
from typing import Generator

import pytest
import sqlalchemy.exc
from efoli import EdifactFormatVersion
from sqlmodel import Session, SQLModel, create_engine, select
from syrupy.assertion import SnapshotAssertion

from fundamend import MigReader
from fundamend.sqlmodels import MessageImplementationGuide as SqlMessageImplementationGuide
from fundamend.sqlmodels import (
    MigDiffLine,
    MigHierarchyMaterialized,
    create_db_and_populate_with_mig_view,
    create_mig_diff_view,
    create_mig_view,
)

from .conftest import is_private_submodule_checked_out, private_submodule_root


@pytest.fixture()
def sqlite_session(tmp_path: Path) -> Generator[Session, None, None]:
    database_path = tmp_path / "test_mig_view.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(bind=engine) as session:
        yield session
        session.commit()
        session.flush()
    print(f"Wrote all data to {database_path.absolute()}")


def test_mig_hierarchy_view_single_mig(sqlite_session: Session) -> None:
    """Test that MIG hierarchy view works for a single MIG file"""
    mig = MigReader(
        Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml"
    ).read()
    sql_mig = SqlMessageImplementationGuide.from_model(mig)
    sqlite_session.add(sql_mig)
    sqlite_session.commit()

    create_mig_view(sqlite_session)

    # Query the materialized view
    statement = (
        select(MigHierarchyMaterialized)
        .where(MigHierarchyMaterialized.format == "UTILTS")
        .order_by(MigHierarchyMaterialized.sort_path)
    )
    results = sqlite_session.exec(statement).all()

    assert len(results) > 0, "Hierarchy should have entries"

    # Check first row
    first_row = results[0]
    assert first_row.format == "UTILTS"
    assert first_row.type in ("segment", "segment_group")

    # Verify computed columns exist
    assert first_row.line_name is not None
    assert first_row.line_status_std is not None


def test_create_db_and_populate_with_mig_view() -> None:
    """Test the convenience function to create and populate MIG database"""
    mig_paths = [Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml"]
    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths)
    assert actual_sqlite_path.exists()

    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        stmt = (
            select(MigHierarchyMaterialized)
            .where(MigHierarchyMaterialized.format == "UTILTS")
            .order_by(MigHierarchyMaterialized.sort_path)
        )
        results = session.exec(stmt).all()

    assert len(results) > 0


@pytest.mark.parametrize("drop_raw_tables", [True, False])
def test_create_db_and_populate_with_mig_view_drop_tables(drop_raw_tables: bool) -> None:
    """Test that drop_raw_tables option works"""
    mig_paths = [Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml"]
    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths, drop_raw_tables=drop_raw_tables)
    assert actual_sqlite_path.exists()

    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        # Check if raw tables exist
        try:
            session.execute(select(SqlMessageImplementationGuide))
            raw_tables_exist = True
        except sqlalchemy.exc.OperationalError:
            raw_tables_exist = False

        if drop_raw_tables:
            assert not raw_tables_exist, "Raw tables should be dropped"
        else:
            assert raw_tables_exist, "Raw tables should exist"


def test_mig_view_with_validity_dates() -> None:
    """Test that validity dates are properly stored"""
    mig_paths = [
        (
            Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml",
            date(2024, 4, 2),
            date(2025, 6, 6),
        )
    ]
    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths)

    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        stmt = select(MigHierarchyMaterialized).where(MigHierarchyMaterialized.format == "UTILTS").limit(1)
        result = session.exec(stmt).first()

    assert result is not None
    assert result.gueltig_von == date(2024, 4, 2)
    assert result.gueltig_bis == date(2025, 6, 6)


def test_mig_diff_view_with_two_versions() -> None:
    """Test MIG diff view with two different versions"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"

    # Find UTILTS MIG files from different format versions
    fv2410_migs = list((private_submodule_root / "FV2410").rglob("**/UTILTS_MIG*.xml"))
    fv2504_migs = list((private_submodule_root / "FV2504").rglob("**/UTILTS_MIG*.xml"))

    if not fv2410_migs or not fv2504_migs:
        pytest.skip("No UTILTS MIG files found in both FV2410 and FV2504")

    mig_paths = [
        (fv2410_migs[0], date(2024, 10, 1), date(2025, 6, 6)),
        (fv2504_migs[0], date(2025, 6, 6), None),
    ]

    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")

    with Session(bind=engine) as session:
        create_mig_diff_view(session)

        # Query the diff view
        stmt = (
            select(MigDiffLine)
            .where(MigDiffLine.old_format == "UTILTS")
            .where(MigDiffLine.new_format == "UTILTS")
            .order_by(MigDiffLine.sort_path)
            .limit(100)
        )
        results = session.exec(stmt).all()

    # Should have some results
    assert len(results) > 0

    # Check that diff_status values are valid
    valid_statuses = {"added", "deleted", "modified", "unchanged"}
    for row in results:
        assert row.diff_status in valid_statuses


def test_mig_hierarchy_all_example_migs(sqlite_session: Session) -> None:
    """Test hierarchy view with all example MIG files"""
    example_files_dir = Path(__file__).parent / "example_files"
    mig_files = list(example_files_dir.glob("*MIG*.xml"))

    for mig_file in mig_files:
        mig = MigReader(mig_file).read()
        sql_mig = SqlMessageImplementationGuide.from_model(mig)
        sqlite_session.add(sql_mig)

    sqlite_session.commit()
    create_mig_view(sqlite_session)

    # Query and verify
    statement = select(MigHierarchyMaterialized).order_by(MigHierarchyMaterialized.sort_path)
    results = sqlite_session.exec(statement).all()

    assert len(results) > 0, "Should have hierarchy entries for all MIGs"


def test_mig_hierarchy_all_from_submodule() -> None:
    """Test hierarchy view with all MIGs from private submodule"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    mig_paths = list(private_submodule_root.rglob("**/*MIG*.xml"))

    if not mig_paths:
        pytest.skip("No MIG files found in submodule")

    # Use just the first few MIGs to keep test reasonable
    mig_paths = mig_paths[:5]

    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths)
    assert actual_sqlite_path.exists()

    engine = create_engine(f"sqlite:///{actual_sqlite_path}")
    with Session(bind=engine) as session:
        stmt = select(MigHierarchyMaterialized).limit(10)
        results = session.exec(stmt).all()

    assert len(results) > 0


@pytest.mark.snapshot
def test_mig_diff_snapshot_comdis(snapshot: SnapshotAssertion) -> None:
    """Snapshot test for MIG diff view comparing COMDIS between FV2410 and FV2504"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    fv2410_comdis = private_submodule_root / "FV2410" / "COMDIS_MIG_1_0d__außerordentliche_20240726.xml"
    fv2504_comdis = private_submodule_root / "FV2504" / "COMDIS_MIG_1_0e__20240619.xml"

    if not fv2410_comdis.exists() or not fv2504_comdis.exists():
        pytest.skip("COMDIS MIG files not found in both FV2410 and FV2504")

    mig_paths = [
        (fv2410_comdis, date(2024, 10, 1), date(2025, 6, 6)),
        (fv2504_comdis, date(2025, 6, 6), None),
    ]

    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")

    with Session(bind=engine) as session:
        create_mig_diff_view(session)

        stmt = (
            select(MigDiffLine)
            .where(MigDiffLine.old_format_version == EdifactFormatVersion.FV2410)
            .where(MigDiffLine.new_format_version == EdifactFormatVersion.FV2504)
            .where(MigDiffLine.old_format == "COMDIS")
            .where(MigDiffLine.new_format == "COMDIS")
            .where(MigDiffLine.diff_status != "unchanged")
            .order_by(MigDiffLine.sort_path)
        )
        results = session.exec(stmt).all()

    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    snapshot.assert_match(raw_results)


@pytest.mark.snapshot
def test_mig_diff_snapshot_pricat(snapshot: SnapshotAssertion) -> None:
    """Snapshot test for MIG diff view comparing PRICAT between FV2410 and FV2504 (larger diff)"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    fv2410_pricat = private_submodule_root / "FV2410" / "PRICAT_MIG_2_0c_Fehlerkorrektur_20240617.xml"
    fv2504_pricat = private_submodule_root / "FV2504" / "PRICAT_MIG_2_0d_20240619.xml"

    if not fv2410_pricat.exists() or not fv2504_pricat.exists():
        pytest.skip("PRICAT MIG files not found in both FV2410 and FV2504")

    mig_paths = [
        (fv2410_pricat, date(2024, 10, 1), date(2025, 6, 6)),
        (fv2504_pricat, date(2025, 6, 6), None),
    ]

    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")

    with Session(bind=engine) as session:
        create_mig_diff_view(session)

        stmt = (
            select(MigDiffLine)
            .where(MigDiffLine.old_format_version == EdifactFormatVersion.FV2410)
            .where(MigDiffLine.new_format_version == EdifactFormatVersion.FV2504)
            .where(MigDiffLine.old_format == "PRICAT")
            .where(MigDiffLine.new_format == "PRICAT")
            .where(MigDiffLine.diff_status != "unchanged")
            .order_by(MigDiffLine.sort_path)
        )
        results = session.exec(stmt).all()

    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    snapshot.assert_match(raw_results)


@pytest.mark.snapshot
def test_mig_diff_snapshot_iftsta(snapshot: SnapshotAssertion) -> None:
    """Snapshot test for MIG diff view comparing IFTSTA between FV2504 and FV2510 (version 2.0f vs 2.0g)"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")

    fv2504_iftsta = private_submodule_root / "FV2504" / "IFTSTA_MIG_2_0f_Fehlerkorrektur_20250225.xml"
    fv2510_iftsta = private_submodule_root / "FV2510" / "IFTSTA_MIG_2_0g_20250401.xml"

    if not fv2504_iftsta.exists() or not fv2510_iftsta.exists():
        pytest.skip("IFTSTA MIG files not found in both FV2504 and FV2510")

    mig_paths = [
        (fv2504_iftsta, date(2025, 6, 6), date(2025, 10, 1)),
        (fv2510_iftsta, date(2025, 10, 1), None),
    ]

    actual_sqlite_path = create_db_and_populate_with_mig_view(mig_files=mig_paths, drop_raw_tables=False)
    engine = create_engine(f"sqlite:///{actual_sqlite_path}")

    with Session(bind=engine) as session:
        create_mig_diff_view(session)

        stmt = (
            select(MigDiffLine)
            .where(MigDiffLine.old_format_version == EdifactFormatVersion.FV2504)
            .where(MigDiffLine.new_format_version == EdifactFormatVersion.FV2510)
            .where(MigDiffLine.old_format == "IFTSTA")
            .where(MigDiffLine.new_format == "IFTSTA")
            .where(MigDiffLine.diff_status != "unchanged")
            .order_by(MigDiffLine.sort_path)
        )
        results = session.exec(stmt).all()

    raw_results = [r.model_dump(mode="json", exclude_none=True) for r in results]
    snapshot.assert_match(raw_results)
