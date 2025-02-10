"""
we try to fill a database using kohlrahbi[sqlmodels] and the data from the machine-readable AHB submodule
"""

from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from fundamend import AhbReader
from fundamend.models.anwendungshandbuch import Anwendungshandbuch as PydanticAnwendunghandbuch
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


def test_sqlmodels_all_anwendungshandbuch(sqlite_session: Session) -> None:
    if not is_private_submodule_checked_out():
        pytest.skip("Skipping test because of missing private submodule")
    private_submodule_root = Path(__file__).parent.parent / "xml-migs-and-ahbs"
    assert private_submodule_root.exists() and private_submodule_root.is_dir()
    for ahb_file_path in private_submodule_root.rglob("**/*AHB*.xml"):
        ahb = AhbReader(ahb_file_path).read()
        roundtrip_abb = _load_anwendungshandbuch_ahb_to_and_from_db(sqlite_session, ahb)
        assert roundtrip_abb == ahb
