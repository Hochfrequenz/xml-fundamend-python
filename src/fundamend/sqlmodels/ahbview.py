"""
helper module to create a "materialized view" (in sqlite this means: create and populate a plain table)
"""

import logging
import tempfile
import uuid
from datetime import date
from itertools import groupby
from pathlib import Path
from typing import Iterable, Literal, Optional
from uuid import UUID

import sqlalchemy
from efoli import EdifactFormatVersion, get_edifact_format_version
from pydantic import BaseModel

try:
    from sqlalchemy.sql.functions import func
    from sqlmodel import Field, Session, SQLModel, create_engine, select
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    # sqlmodel is only an optional dependency when fundamend is used to fill a database
    raise

from fundamend import AhbReader
from fundamend import Anwendungshandbuch as PydanticAnwendungshandbuch
from fundamend.sqlmodels.anwendungshandbuch import (
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
from fundamend.sqlmodels.internals import _execute_bare_sql

_logger = logging.getLogger(__name__)


def create_ahb_view(session: Session) -> None:
    """
    Create a materialized view for the Anwendungshandbücher using a SQLAlchemy session.
    Warning: This is only tested for SQLite!
    """
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "materialize_ahb_view.sql")

    number_of_inserted_rows = session.scalar(
        select(func.count(AhbHierarchyMaterialized.id))  # type:ignore[arg-type] # pylint:disable=not-callable #
    )
    _logger.info(
        "Inserted %d rows into the materialized view %s",
        number_of_inserted_rows,
        AhbHierarchyMaterialized.__tablename__,
    )


class _PruefiValidity(BaseModel):
    """
    models how long a model, associated with a pruefidentifikator is valid
    """

    gueltig_von: Optional[date]  # inclusive start
    gueltig_bis: Optional[date]  # exclusive end
    pruefidentifikator: str

    def overlaps(self, other: "_PruefiValidity") -> bool:
        """
        returns true if the two validity periods overlap
        """
        return (
            (self.gueltig_bis is None or other.gueltig_von is None or self.gueltig_bis > other.gueltig_von)
            and (self.gueltig_von is None or other.gueltig_bis is None or self.gueltig_von < other.gueltig_bis)
            or (self.gueltig_bis is None and other.gueltig_bis is None)
            or (self.gueltig_von is None and other.gueltig_von is None)
        )


def _check_for_no_overlaps(pruefi_validities: list[_PruefiValidity]) -> None:
    """raises a value error if there are duplicates/redundancies"""
    duplicate_pruefis_for_same_gueltigkeitszeitraum = []

    for duplicate_pruefi, group in groupby(
        sorted(pruefi_validities, key=lambda x: x.pruefidentifikator), key=lambda x: x.pruefidentifikator
    ):
        group_list = list(group)
        if any(a.overlaps(b) for a, b in zip(group_list, group_list[1:])):
            duplicate_pruefis_for_same_gueltigkeitszeitraum.append(duplicate_pruefi)
    if any(duplicate_pruefis_for_same_gueltigkeitszeitraum):
        raise ValueError(
            # pylint:disable=line-too-long
            f"There are duplicate pruefidentifikators in the AHBs: {', '.join(duplicate_pruefis_for_same_gueltigkeitszeitraum)}. Dropping the source tables is not a good idea."
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
    pruefis_added: list[_PruefiValidity] = []
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
                sql_ahb.edifact_format_version = get_edifact_format_version(sql_ahb.gueltig_von)
            session.add(sql_ahb)
            pruefis_added += [
                _PruefiValidity(
                    pruefidentifikator=af.pruefidentifikator, gueltig_bis=gueltig_bis, gueltig_von=gueltig_von
                )
                for af in sql_ahb.anwendungsfaelle
            ]
        session.commit()
        session.flush()
        create_ahb_view(session)
        if drop_raw_tables:
            _check_for_no_overlaps(pruefis_added)
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


class AhbHierarchyMaterialized(SQLModel, table=True):
    """
    A materialized flattened AHB hierarchy containing segment groups, segments, data elements, codes,
    and enriched with metadata like format, versionsnummer, and prüfidentifikator.
    This table is not thought to be written to, but only read from.
    It is created once after all other tables have been filled by the create_ahb_view function in ahbview.py.
    """

    __tablename__ = "ahb_hierarchy_materialized"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    anwendungsfall_pk: UUID = Field(index=True)
    anwendungshandbuch_primary_key: UUID = Field(index=True)
    current_id: UUID
    root_id: UUID
    parent_id: Optional[UUID] = None
    depth: int
    position: Optional[int] = Field(default=None)
    path: str
    id_path: str
    parent_path: str
    root_order: int
    type: str = Field(index=True)
    source_id: UUID
    sort_path: str = Field(index=True)

    # Metadata
    pruefidentifikator: str = Field(index=True)
    format: str = Field(index=True)
    versionsnummer: str = Field(index=True)
    gueltig_von: Optional[date] = Field(default=None, index=True)
    gueltig_bis: Optional[date] = Field(default=None, index=True)
    kommunikation_von: Optional[str] = Field(default=None, index=True)
    beschreibung: Optional[str] = Field(default=None, index=True)
    edifact_format_version: Optional[EdifactFormatVersion] = Field(default=None, index=True)

    # Segment Group
    segmentgroup_id: Optional[str] = Field(default=None, index=True)
    segmentgroup_name: Optional[str] = Field(default=None, index=True)
    segmentgroup_ahb_status: Optional[str] = Field(default=None)
    segmentgroup_position: Optional[int] = Field(default=None, index=True)
    segmentgroup_anwendungsfall_primary_key: Optional[UUID] = Field(default=None)

    # Segment
    segment_id: Optional[str] = Field(default=None, index=True)
    segment_name: Optional[str] = Field(default=None, index=True)
    segment_number: Optional[str] = Field(default=None, index=True)
    segment_ahb_status: Optional[str] = Field(default=None)
    segment_position: Optional[int] = Field(default=None, index=True)
    is_on_uebertragungsdatei_level: Optional[bool] = Field(default=None, index=False)

    # Data Element Group
    dataelementgroup_id: Optional[str] = Field(default=None, index=True)
    dataelementgroup_name: Optional[str] = Field(default=None, index=True)
    dataelementgroup_position: Optional[int] = Field(default=None, index=True)

    # Data Element
    dataelement_id: Optional[str] = Field(default=None, index=True)
    dataelement_name: Optional[str] = Field(default=None, index=True)
    dataelement_position: Optional[int] = Field(default=None, index=True)
    dataelement_ahb_status: Optional[str] = Field(default=None, index=True)

    # Code
    code_id: Optional[UUID] = Field(default=None, index=True)
    code_name: Optional[str] = Field(default=None, index=True)
    code_description: Optional[str] = Field(default=None, index=True)
    code_value: Optional[str] = Field(default=None, index=True)
    code_ahb_status: Optional[str] = Field(default=None, index=True)
    code_position: Optional[int] = Field(default=None, index=True)


__all__ = ["AhbHierarchyMaterialized", "create_db_and_populate_with_ahb_view", "create_ahb_view"]
