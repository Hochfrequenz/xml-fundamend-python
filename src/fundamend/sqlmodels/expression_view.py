"""
helper module to create a "materialized view" (in sqlite this means: create and populate a plain table)
"""

import asyncio
import logging
import typing
import uuid

from efoli import EdifactFormatVersion

from fundamend.sqlmodels import AhbHierarchyMaterialized, Bedingung
from fundamend.sqlmodels.anwendungshandbuch import Paket, UbBedingung

try:
    from sqlalchemy.sql.functions import func
    from sqlmodel import Field, Session, SQLModel, UniqueConstraint, col, select

except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    # sqlmodel is only an optional dependency when fundamend is used to fill a database
    raise

try:
    from ahbicht.expressions.condition_expression_parser import extract_categorized_keys
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels,ahbicht]?"
    # sqlmodel and ahbicht are only optional dependencies when fundamend is used to fill a database
    raise

_logger = logging.getLogger(__name__)


def _generate_node_texts(session: Session, expression: str, ahb_pk: uuid.UUID) -> str:
    categorized_key_extract = asyncio.run(extract_categorized_keys(expression))
    bedingung_keys = (
        categorized_key_extract.format_constraint_keys
        + categorized_key_extract.requirement_constraint_keys
        + categorized_key_extract.hint_keys
    )
    paket_keys = categorized_key_extract.package_keys
    ubbedingung_keys = categorized_key_extract.time_condition_keys
    # probably, we'd be faster if we just loaded all pakete and all bedingungen once instead of selecting over and over
    # again for each expression
    bedingungen = {
        x.nummer: x.text
        for x in session.exec(
            select(Bedingung).where(
                col(Bedingung.nummer).in_(bedingung_keys),  # pylint:disable=no-member
                Bedingung.anwendungshandbuch_primary_key == ahb_pk,
            )
        ).all()
    }
    pakete = {
        x.nummer: x.text
        for x in session.exec(
            select(Paket).where(
                col(Paket.nummer).in_(paket_keys), Paket.anwendungshandbuch_primary_key == ahb_pk  # pylint:disable=no-member
            )
        ).all()
    }
    ubbedingungen = {
        x.nummer: x.text
        for x in session.exec(
            select(UbBedingung).where(
                col(UbBedingung.nummer).in_(ubbedingung_keys),  # pylint:disable=no-member
                UbBedingung.anwendungshandbuch_primary_key == ahb_pk,
            )
        ).all()
    }
    joined_dict = {**bedingungen, **pakete, **ubbedingungen}
    node_texts = "\n".join([f"[{key}] {value}" for key, value in joined_dict.items()])
    return node_texts


@typing.no_type_check
def create_and_fill_ahb_expression_table(session: Session) -> None:
    """
    creates and fills the ahb_expressions table. It uses the ahb_hierarchy_materialized table to extract all expressions
    and parses each expression with ahbicht. The latter has to be done in Python.
    """
    rows = []

    for col in [
        AhbHierarchyMaterialized.segmentgroup_ahb_status,
        AhbHierarchyMaterialized.segment_ahb_status,
        AhbHierarchyMaterialized.dataelement_ahb_status,
        AhbHierarchyMaterialized.code_ahb_status,
    ]:
        stmt = select(
            AhbHierarchyMaterialized.edifact_format_version,
            AhbHierarchyMaterialized.format,
            AhbHierarchyMaterialized.pruefidentifikator,
            col,
            AhbHierarchyMaterialized.anwendungshandbuch_primary_key,
        )
        rows.extend(session.exec(stmt))

    seen: set[tuple[str, str, str, str]] = set()
    for row in rows:
        if not row[3] or not row[3].strip():
            continue
        expression = row[3].strip()
        key = (row[0], row[1], row[2], expression)
        similar_entry_has_been_handled = key in seen
        if similar_entry_has_been_handled:
            continue
        seen.add(key)
        ahb_expression_row = AhbExpression(
            edifact_format_version=row[0],
            format=row[1],
            pruefidentifikator=row[2],
            expression=expression,
            node_texts=_generate_node_texts(session, expression, row.anwendungshandbuch_primary_key),
            anwendungshandbuch_primary_key=row[4],
        )
        session.add(ahb_expression_row)
    number_of_inserted_rows = session.scalar(select(func.count(AhbExpression.id)))  # pylint:disable=not-callable
    _logger.info(
        "Inserted %d rows into the table %s",
        number_of_inserted_rows,
        AhbExpression.__tablename__,
    )
    session.commit()


class AhbExpression(SQLModel, table=True):
    """
    A table that contains all expressions that are used in any AHB, each with prüfidentifikator and format_version.
    It's created by UNIONing all 'ahb_status' columns from all relevant tables.
    Additionally, this table has a column that resolves the expression to a human-readable text.
    """

    __tablename__ = "ahb_expressions"
    __table_args__ = (
        UniqueConstraint(
            "edifact_format_version",
            "format",
            "pruefidentifikator",
            "expression",
            name="idx_ahb_expressions_metadata_expression",
        ),
    )
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    edifact_format_version: EdifactFormatVersion = Field(index=True)
    format: str = Field(index=True)  # the edifact format, e.g. 'UTILMD'
    pruefidentifikator: str | None = Field(index=True, default=None)  # might be None for CONTRL or APERAK
    expression: str = Field(index=True)  #: e.g 'Muss [1] U [2]'
    node_texts: str = Field()
    """
    this contains the typical "[1] Foo Text\n[2] Bar Text" which explains the meaning of the nodes from inside the
    respective Expression (e.g. for expression "Muss [1] U [2]")
    """
    anwendungshandbuch_primary_key: uuid.UUID = Field()
