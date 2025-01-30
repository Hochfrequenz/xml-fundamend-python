"""
we try to fill a database using kohlrahbi[sqlmodels] and the data from the machine-readable AHB submodule
"""

import json
from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from fundamend import AhbReader
from fundamend.sqlmodels.anwendungshandbuch import Anwendungshandbuch


@pytest.fixture()
def sqlite_session(tmp_path: Path) -> Generator[Session, None, None]:
    database_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{database_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(bind=engine) as session:
        yield session


def _load_anwendungshandbuch_ahb_to_db(session: Session, json_path: Path) -> None:
    with open(json_path, "r", encoding="utf-8") as json_file:
        file_body = json.loads(json_file.read())
    ahb = Anwendungshandbuch.model_validate(file_body)
    return None


def test_sqlmodels_anwendungshandbuch(sqlite_session: Session, tmp_path: Path) -> None:
    ahb = AhbReader(
        Path(__file__).parent / "example_files" / "UTILTS_AHB_1.1d_Konsultationsfassung_2024_04_02.xml"
    ).read()
    ahb_json_file_path = tmp_path / "utilts_ahb1.1.json"
    with open(ahb_json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(ahb.model_dump(mode="json"), json_file, indent=2, ensure_ascii=False)
    _load_anwendungshandbuch_ahb_to_db(sqlite_session, ahb_json_file_path)
