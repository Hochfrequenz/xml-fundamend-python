"""
helper module to create a "materialized view" (in sqlite this means: create and populate a plain table)
"""

import asyncio
import logging
import uuid
from pathlib import Path
from uuid import UUID

from efoli import EdifactFormatVersion

from fundamend.sqlmodels import Bedingung
from fundamend.sqlmodels.anwendungshandbuch import UbBedingung, Paket
from fundamend.sqlmodels.internals import _execute_bare_sql

try:
    from sqlalchemy.sql.functions import func
    from sqlmodel import Field, Session, SQLModel, create_engine, select
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


def _generate_node_texts(session: Session, expression: str) -> str:
    categorized_key_extract = asyncio.run(extract_categorized_keys(expression))
    bedingung_keys = (
        categorized_key_extract.format_constraint_keys
        + categorized_key_extract.requirement_constraint_keys
        + categorized_key_extract.hint_keys
    )
    paket_keys = categorized_key_extract.package_keys
    ubbedingung_keys = categorized_key_extract.time_condition_keys
    # maybe it's faster to just load all pakete and all bedingungen once instead of re-selecting for each expression
    bedingungen = {
        x.nummer: x.text for x in session.exec(select(Bedingung).where(Bedingung.nummer.in_(bedingung_keys)).all())
    }
    pakete = {x.nummer: x.text for x in session.exec(select(Paket).where(Bedingung.nummer.in_(paket_keys)).all())}
    ubbedingungen = {
        x.nummer: x.text for x in session.exec(select(UbBedingung).where(Bedingung.nummer.in_(ubbedingung_keys)).all())
    }
    joined_dict = {**bedingungen, **pakete, **ubbedingungen}
    node_texts = "\n".join([f"[{key}] {value}" for key, value in joined_dict.items()])
    return node_texts


def create_and_fill_ahb_expression_table(session: Session) -> None:
    """
    creates and fills the ahb_expressions table. It uses the ahb_hierarchy_materialized table to extract all expressions
    and parses each expression with ahbicht. The latter has to be done in Python.
    """
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "create_ahb_expressions_table.sql")

    number_of_inserted_rows = session.scalar(
        select(func.count(AhbExpression.id))  # type:ignore[arg-type] # pylint:disable=not-callable
    )
    _logger.info(
        "Inserted %d rows into the table %s",
        number_of_inserted_rows,
        AhbExpression.__tablename__,
    )
    for row in session.exec(select(AhbExpression)).all():
        row.node_texts = _generate_node_texts(session, row.expression)
        session.add(row)
    session.commit()


class AhbExpression(SQLModel, table=True):
    """
    A table that contains all expressions that are used in any AHB, each with prüfidentifikator and format_version.
    It's created by UNIONing all 'ahb_status' columns from all relevant tables.
    Additionally, this table has a column that resolves the expression to a human-readable text.
    """

    __tablename__ = "ahb_expressions"
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    edifact_format_version: EdifactFormatVersion = Field(index=True)
    format: str = Field(index=True)  # the edifact format, e.g. 'UTILMD'
    pruefidentifikator: str | None = Field(index=True, default=None)  # might be None for CONTRL or APERAK
    expression: str = Field(index=True)  #: e.g 'Muss [1] U [2]'
    node_texts: str = Field(index=True)
    anwendungshandbuch_primary_key:UUID = Field()
    """
    this contains the typical "[1] Foo Text\n[2] Bar Text" which explains the meaning of the nodes from inside the
    respective Expression (e.g. for expression "Muss [1] U [2]")
    """
