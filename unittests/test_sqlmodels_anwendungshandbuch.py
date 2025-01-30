"""
we try to fill a database using kohlrahbi[sqlmodels] and the data from the machine-readable AHB submodule
"""

import json
from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from fundamend import AhbReader
from fundamend.models.anwendungshandbuch import Anwendungshandbuch as PydanticAnwendunghandbuch
from fundamend.sqlmodels.anwendungshandbuch import Anwendungshandbuch


@pytest.fixture()
def sqlite_session(tmp_path: Path) -> Generator[Session, None, None]:
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(bind=engine) as session:
        yield session


def _load_anwendungshandbuch_ahb_to_and_from_db(
    session: Session, pydantic_ahb: PydanticAnwendunghandbuch
) -> PydanticAnwendunghandbuch:
    sql_ahb = Anwendungshandbuch.from_model(pydantic_ahb)
    session.add(sql_ahb)
    session.commit()
    session.refresh(sql_ahb)
    pydantic_ahb_after_roundtrip = sql_ahb.to_model()
    return pydantic_ahb_after_roundtrip


def test_sqlmodels_anwendungshandbuch(sqlite_session: Session, tmp_path: Path) -> None:
    ahb = AhbReader(
        Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    ).read()
    roundtrip_abb = _load_anwendungshandbuch_ahb_to_and_from_db(sqlite_session, ahb)
    assert roundtrip_abb == ahb
