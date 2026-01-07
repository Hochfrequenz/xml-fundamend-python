"""
Tests for MIG SQLModels - we try to fill a database and roundtrip the data
"""

from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from fundamend import MigReader
from fundamend.models.messageimplementationguide import MessageImplementationGuide as PydanticMessageImplementationGuide
from fundamend.sqlmodels import MessageImplementationGuide as SqlMessageImplementationGuide

from .conftest import is_private_submodule_checked_out


@pytest.fixture()
def sqlite_session(tmp_path: Path) -> Generator[Session, None, None]:
    database_path = tmp_path / "test_mig.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(bind=engine) as session:
        yield session
        session.commit()
    print(f"Wrote all data to {database_path.absolute()}")


def _load_mig_to_and_from_db(
    session: Session, pydantic_mig: PydanticMessageImplementationGuide
) -> PydanticMessageImplementationGuide:
    sql_mig = SqlMessageImplementationGuide.from_model(pydantic_mig)
    session.add(sql_mig)
    session.commit()
    session.refresh(sql_mig)
    pydantic_mig_after_roundtrip = sql_mig.to_model()
    return pydantic_mig_after_roundtrip


def test_sqlmodels_single_mig(sqlite_session: Session) -> None:
    mig = MigReader(
        Path(__file__).parent / "example_files" / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02.xml"
    ).read()
    roundtrip_mig = _load_mig_to_and_from_db(sqlite_session, mig)
    mig_json = mig.model_dump(mode="json")
    roundtrip_json = roundtrip_mig.model_dump(mode="json")
    assert mig_json == roundtrip_json  # in pycharm the error message is much better when comparing plain python dicts
    assert roundtrip_mig == mig


def test_sqlmodels_mig_with_uebertragungsdatei(sqlite_session: Session) -> None:
    mig = MigReader(
        Path(__file__).parent
        / "example_files"
        / "UTILTS_MIG_1.1d_Konsultationsfassung_2024_04_02_with_Uebertragungsdatei.xml"
    ).read()
    roundtrip_mig = _load_mig_to_and_from_db(sqlite_session, mig)
    mig_json = mig.model_dump(mode="json")
    roundtrip_json = roundtrip_mig.model_dump(mode="json")
    assert mig_json == roundtrip_json
    assert roundtrip_mig == mig


def test_sqlmodels_all_example_migs(sqlite_session: Session) -> None:
    """Test all MIG files in example_files directory"""
    example_files_dir = Path(__file__).parent / "example_files"
    for mig_file_path in example_files_dir.glob("*MIG*.xml"):
        mig = MigReader(mig_file_path).read()
        roundtrip_mig = _load_mig_to_and_from_db(sqlite_session, mig)
        assert roundtrip_mig == mig, f"Roundtrip failed for {mig_file_path.name}"


def test_sqlmodels_all_migs_from_submodule(sqlite_session: Session) -> None:
    """Test all MIGs from the private submodule (skipped if not checked out)"""
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    for mig_file_path in private_submodule_root.rglob("**/*MIG*.xml"):
        mig = MigReader(mig_file_path).read()
        roundtrip_mig = _load_mig_to_and_from_db(sqlite_session, mig)
        assert roundtrip_mig == mig, f"Roundtrip failed for {mig_file_path}"
