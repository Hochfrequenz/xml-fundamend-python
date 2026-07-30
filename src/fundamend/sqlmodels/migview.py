"""
Helper module to create a "materialized view" for MIGs (Message Implementation Guides).
In SQLite this means: create and populate a plain table.
"""

# pylint: disable=duplicate-code
# This module intentionally follows the same patterns as ahbview.py

import logging
import tempfile
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Literal
from uuid import UUID

import sqlalchemy
from efoli import EdifactFormat, EdifactFormatVersion, get_edifact_format_version
from sqlalchemy.sql.elements import TextClause

try:
    from sqlalchemy.sql.functions import func
    from sqlmodel import Field, Session, SQLModel, create_engine, select
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    raise

from fundamend import MessageImplementationGuide as PydanticMessageImplementationGuide
from fundamend import MigReader
from fundamend.sqlmodels.internals import _execute_bare_sql
from fundamend.sqlmodels.messageimplementationguide import MessageImplementationGuide as SqlMessageImplementationGuide
from fundamend.sqlmodels.messageimplementationguide import (
    MigCode,
    MigDataElement,
    MigDataElementGroup,
    MigSegment,
    MigSegmentGroup,
    MigSegmentGroupLink,
)

_logger = logging.getLogger(__name__)


def create_mig_view(session: Session) -> None:
    """
    Create a materialized view for the Message Implementation Guides using a SQLAlchemy session.
    Warning: This is only tested for SQLite!
    """
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "materialize_mig_view.sql")

    number_of_inserted_rows = session.scalar(
        select(func.count(MigHierarchyMaterialized.id))  # type: ignore[arg-type] # pylint:disable=not-callable
    )
    _logger.info(
        "Inserted %d rows into the materialized view %s",
        number_of_inserted_rows,
        MigHierarchyMaterialized.__tablename__,
    )


_before_bulk_insert_ops: list[TextClause] = [
    sqlalchemy.text("PRAGMA synchronous = OFF"),
    sqlalchemy.text("PRAGMA journal_mode = WAL"),
    sqlalchemy.text("PRAGMA cache_size = -64000"),
    sqlalchemy.text("PRAGMA temp_store = MEMORY"),
    sqlalchemy.text("PRAGMA locking_mode = EXCLUSIVE"),
]
_after_bulk_insert_ops: list[TextClause] = [
    sqlalchemy.text("PRAGMA wal_checkpoint(FULL)"),
    sqlalchemy.text("PRAGMA journal_mode = DELETE"),
    sqlalchemy.text("PRAGMA locking_mode = NORMAL"),
    sqlalchemy.text("PRAGMA synchronous = FULL"),
]


def create_db_and_populate_with_mig_view(
    mig_files: Iterable[Path | tuple[Path, date, date | None] | tuple[Path, Literal[None], Literal[None]]],
    drop_raw_tables: bool = False,
) -> Path:
    """
    Creates a SQLite database as temporary file, populates it with the MIGs provided and materializes the MIG view.
    You may provide either paths to the MIG.xml files or tuples where each Path comes with a gueltig_von and gueltig_bis
    date.
    Optionally deletes the original tables to have a smaller db file.
    Returns the path to the temporary database file.
    The calling code should move the file to a permanent location if needed.
    """
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as sqlite_file:
        sqlite_path = Path(sqlite_file.name)
    engine = create_engine(f"sqlite:///{sqlite_path}")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with engine.connect() as conn:
        for _op in _before_bulk_insert_ops:
            conn.execute(_op)
        conn.commit()

    with Session(bind=engine) as session:
        sql_migs: list[SqlMessageImplementationGuide] = []
        for item in mig_files:
            mig: PydanticMessageImplementationGuide
            gueltig_von: date | None
            gueltig_bis: date | None
            if isinstance(item, Path):
                mig = MigReader(item).read()
                gueltig_von = None
                gueltig_bis = None
            elif isinstance(item, tuple):
                mig = MigReader(item[0]).read()
                gueltig_von = item[1]
                gueltig_bis = item[2]
            else:
                raise ValueError(f"Invalid item type in mig_files: {type(item)}")
            sql_mig = SqlMessageImplementationGuide.from_model(mig)
            sql_mig.gueltig_von = gueltig_von
            sql_mig.gueltig_bis = gueltig_bis
            if sql_mig.gueltig_von is not None:
                sql_mig.edifact_format_version = get_edifact_format_version(sql_mig.gueltig_von)
            sql_migs.append(sql_mig)
        session.add_all(sql_migs)
        session.commit()

    with engine.connect() as conn:
        for _op in _after_bulk_insert_ops:
            conn.execute(_op)
        conn.commit()

    with Session(bind=engine) as session:
        create_mig_view(session)
        if drop_raw_tables:
            for model_class in [
                SqlMessageImplementationGuide,
                MigCode,
                MigDataElement,
                MigDataElementGroup,
                MigSegment,
                MigSegmentGroup,
                MigSegmentGroupLink,
            ]:
                session.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {model_class.__tablename__};"))
                _logger.debug("Dropped %s", model_class.__tablename__)
        session.commit()

    return sqlite_path


class MigHierarchyMaterialized(SQLModel, table=True):
    """
    A materialized flattened MIG hierarchy containing segment groups, segments, data elements, codes,
    and enriched with metadata like format and versionsnummer.
    This table is not thought to be written to, but only read from.
    It is created once after all other tables have been filled by the create_mig_view function.
    """

    __tablename__ = "mig_hierarchy_materialized"

    id: str = Field(primary_key=True)
    mig_pk: UUID = Field(index=True)
    current_id: UUID
    root_id: UUID
    parent_id: UUID | None = None
    depth: int
    position: int | None = Field(default=None)
    path: str
    id_path: str = Field(index=True)
    parent_path: str
    root_order: int
    type: str = Field(index=True)
    source_id: UUID
    sort_path: str = Field(index=True)

    # Metadata
    format: EdifactFormat = Field(index=True)
    versionsnummer: str = Field(index=True)
    gueltig_von: date | None = Field(default=None, index=True)
    gueltig_bis: date | None = Field(default=None, index=True)
    edifact_format_version: EdifactFormatVersion | None = Field(default=None, index=True)
    is_on_uebertragungsdatei_level: bool | None = Field(default=None)

    # Segment Group
    segmentgroup_id: str | None = Field(default=None, index=True)
    segmentgroup_name: str | None = Field(default=None, index=True)
    segmentgroup_status_std: str | None = Field(default=None)
    segmentgroup_status_specification: str | None = Field(default=None)
    segmentgroup_counter: str | None = Field(default=None)
    segmentgroup_level: int | None = Field(default=None)
    segmentgroup_max_rep_std: int | None = Field(default=None)
    segmentgroup_max_rep_specification: int | None = Field(default=None)
    segmentgroup_position: int | None = Field(default=None, index=True)

    # Segment
    segment_id: str | None = Field(default=None, index=True)
    segment_name: str | None = Field(default=None, index=True)
    segment_status_std: str | None = Field(default=None)
    segment_status_specification: str | None = Field(default=None)
    segment_counter: str | None = Field(default=None)
    segment_level: int | None = Field(default=None)
    segment_number: str | None = Field(default=None, index=True)
    segment_max_rep_std: int | None = Field(default=None)
    segment_max_rep_specification: int | None = Field(default=None)
    segment_example: str | None = Field(default=None)
    segment_description: str | None = Field(default=None)
    segment_position: int | None = Field(default=None, index=True)

    # Data Element Group
    dataelementgroup_id: str | None = Field(default=None, index=True)
    dataelementgroup_name: str | None = Field(default=None, index=True)
    dataelementgroup_description: str | None = Field(default=None)
    dataelementgroup_status_std: str | None = Field(default=None)
    dataelementgroup_status_specification: str | None = Field(default=None)
    dataelementgroup_position: int | None = Field(default=None, index=True)

    # Data Element
    dataelement_id: str | None = Field(default=None, index=True)
    dataelement_name: str | None = Field(default=None, index=True)
    dataelement_description: str | None = Field(default=None)
    dataelement_status_std: str | None = Field(default=None, index=True)
    dataelement_status_specification: str | None = Field(default=None, index=True)
    dataelement_format_std: str | None = Field(default=None)
    dataelement_format_specification: str | None = Field(default=None)
    dataelement_position: int | None = Field(default=None, index=True)

    # Code
    code_id: UUID | None = Field(default=None, index=True)
    code_name: str | None = Field(default=None, index=True)
    code_description: str | None = Field(default=None, index=True)
    code_value: str | None = Field(default=None, index=True)
    code_position: int | None = Field(default=None, index=True)

    # Computed columns
    line_name: str | None = Field(default=None, index=True)
    line_status_std: str | None = Field(default=None, index=True)
    line_status_specification: str | None = Field(default=None, index=True)


__all__ = ["MigHierarchyMaterialized", "create_db_and_populate_with_mig_view", "create_mig_view"]
