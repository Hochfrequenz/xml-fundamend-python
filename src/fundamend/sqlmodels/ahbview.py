"""
helper module to create a "materialized view" (in sqlite this means: create and populate a plain table)
"""

import logging
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Iterable, Literal, Optional

import sqlalchemy
from efoli import get_edifact_format_version
from sqlalchemy.sql.functions import func
from sqlmodel import Session, SQLModel, create_engine, select

from fundamend import AhbReader
from fundamend import Anwendungshandbuch as PydanticAnwendungshandbuch
from fundamend.sqlmodels.anwendungshandbuch import (
    AhbHierarchyMaterialized,
    Anwendungsfall,
)
from fundamend.sqlmodels.anwendungshandbuch import Anwendungshandbuch as SqlAnwendungshandbuch
from fundamend.sqlmodels.anwendungshandbuch import (
    Code,
    DataElement,
    DataElementGroup,
    Segment,
    SegmentGroup,
    SegmentGroupLink,
)

_logger = logging.getLogger(__name__)


def create_ahb_view(session: Session) -> None:
    """
    Create a materialized view for the Anwendungshandbücher using a SQLAlchemy session.
    Warning: This is only tested for SQLite!
    """
    path_to_sql_command = Path(__file__).parent / "materialize_ahb_view.sql"

    with open(path_to_sql_command, "r", encoding="utf-8") as sql_file:
        bare_sql = sql_file.read()

    bare_statements = bare_sql.split(";")

    for bare_statement in bare_statements:
        statement = bare_statement.strip()
        if statement:
            session.execute(sqlalchemy.text(statement))
    session.commit()
    number_of_inserted_rows = session.scalar(
        select(func.count(AhbHierarchyMaterialized.id))  # type:ignore[arg-type] # pylint:disable=not-callable #
    )
    _logger.info(
        "Inserted %d rows into the materialized view %s",
        number_of_inserted_rows,
        AhbHierarchyMaterialized.__tablename__,
    )


def create_db_and_populate_with_ahb_view(
    ahb_files: Iterable[Path | tuple[Path, date, Optional[date]] | tuple[Path, Literal[None], Literal[None]]],
    drop_raw_tables: bool = False,
) -> Path:
    """
    Creates a SQLite database as temporary file, populates it with the AHBs provided and the materializes the AHB view.
    You may provide either paths to the AHB.xml files or tuples where each Path comes with a gueltig_von and gueltig_bis
    date.
    Optionally deletes the original tables to have a smaller db file (only if the prüfis are unique across all AHBs).
    Returns the path to the temporary database file.
    The calling code should move the file to a permanent location if needed.
    """
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as sqlite_file:
        sqlite_path = Path(sqlite_file.name)
    engine = create_engine(f"sqlite:///{sqlite_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    pruefis_added: list[str] = []
    with Session(bind=engine) as session:
        for item in ahb_files:
            ahb: PydanticAnwendungshandbuch
            gueltig_von: Optional[date]
            gueltig_bis: Optional[date]
            if isinstance(item, Path):
                ahb = AhbReader(item).read()
                gueltig_von = None
                gueltig_bis = None
            elif isinstance(item, tuple):
                ahb = AhbReader(item[0]).read()
                gueltig_von = item[1]
                gueltig_bis = item[2]
            else:
                raise ValueError(f"Invalid item type in ahb_files: {type(item)}")
            sql_ahb = SqlAnwendungshandbuch.from_model(ahb)
            sql_ahb.gueltig_von = gueltig_von
            sql_ahb.gueltig_bis = gueltig_bis
            if sql_ahb.gueltig_von is not None:
                sql_ahb.edifact_format_version = get_edifact_format_version(gueltig_von)
            session.add(sql_ahb)
            pruefis_added += [af.pruefidentifikator for af in sql_ahb.anwendungsfaelle]
        session.commit()
        session.flush()
        create_ahb_view(session)
        if drop_raw_tables:
            duplicate_pruefis = [item for item, count in Counter(pruefis_added).items() if count > 1]
            if any(duplicate_pruefis):
                raise ValueError(
                    # pylint:disable=line-too-long
                    f"There are duplicate pruefidentifikators in the AHBs: {', '.join(duplicate_pruefis)}. Dropping the source tables is not a good idea."
                )
            for model_class in [
                SqlAnwendungshandbuch,
                Anwendungsfall,
                Code,
                DataElement,
                DataElementGroup,
                Segment,
                SegmentGroup,
                SegmentGroupLink,
            ]:
                session.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {model_class.__tablename__};"))
                _logger.debug("Dropped %s", model_class.__tablename__)
        session.commit()
        session.flush()
    return sqlite_path


__all__ = ["create_db_and_populate_with_ahb_view", "create_ahb_view"]
