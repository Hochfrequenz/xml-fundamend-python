"""
helper module to create a table with a "Bedingung" column like the one in the PDF/docx AHBs
"""

import asyncio
import logging
import uuid
from contextvars import ContextVar
from typing import Optional

from efoli import EdifactFormat, EdifactFormatVersion

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
    import inject
    from ahbicht.content_evaluation.evaluationdatatypes import EvaluatableData, EvaluatableDataProvider
    from ahbicht.content_evaluation.evaluator_factory import create_content_evaluation_result_based_evaluators
    from ahbicht.content_evaluation.expression_check import is_valid_expression
    from ahbicht.content_evaluation.token_logic_provider import SingletonTokenLogicProvider, TokenLogicProvider
    from ahbicht.expressions.condition_expression_parser import extract_categorized_keys
    from ahbicht.models.content_evaluation_result import ContentEvaluationResult, ContentEvaluationResultSchema
    from lark.exceptions import VisitError
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels,ahbicht]?"
    # sqlmodel and ahbicht are only optional dependencies when fundamend is used to fill a database
    raise

_logger = logging.getLogger(__name__)

_content_evaluation_result: ContextVar[Optional[ContentEvaluationResult]] = ContextVar(
    "_content_evaluation_result", default=None
)


def _get_evaluatable_data() -> EvaluatableData[ContentEvaluationResult]:
    """
    returns the _content_evaluation_result context var value wrapped in a EvaluatableData container.
    This is the kind of data that the ContentEvaluationResultBased RC/FC Evaluators, HintsProvider and Package Resolver
    require.
    :return:
    """
    cer = _content_evaluation_result.get()
    return EvaluatableData(
        body=ContentEvaluationResultSchema().dump(cer),
        edifact_format=EdifactFormat.UTILMD,  # not important, something has to be here
        edifact_format_version=EdifactFormatVersion.FV2504,  # not important, something has to be here
    )


def _setup_weird_ahbicht_dependency_injection() -> None:
    def configure(binder: inject.Binder) -> None:
        binder.bind(
            TokenLogicProvider,
            SingletonTokenLogicProvider(
                [*create_content_evaluation_result_based_evaluators(EdifactFormat.UTILMD, EdifactFormatVersion.FV2504)]
            ),
        )
        binder.bind_to_provider(EvaluatableDataProvider, _get_evaluatable_data)

    inject.configure_once(configure)


def _generate_node_texts(session: Session, expression: str, ahb_pk: uuid.UUID) -> str:
    try:
        categorized_key_extract = asyncio.run(extract_categorized_keys(expression))
    except SyntaxError as syntax_error:
        _logger.info("The expression '%s' could not be parsed: %s", expression, syntax_error)
        return ""  # I decided against returning the error message, although it's tempting - but still bad practice
    except VisitError as visit_error:
        _logger.info("The expression '%s' could not be parsed: %s", expression, visit_error)
        return ""
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
                col(Paket.nummer).in_(paket_keys),
                Paket.anwendungshandbuch_primary_key == ahb_pk,  # pylint:disable=no-member
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


def create_and_fill_ahb_expression_table(session: Session) -> None:
    """
    creates and fills the ahb_expressions table. It uses the ahb_hierarchy_materialized table to extract all expressions
    and parses each expression with ahbicht. The latter has to be done in Python.
    """
    rows = []
    _setup_weird_ahbicht_dependency_injection()
    for ahb_status_col in [
        AhbHierarchyMaterialized.segmentgroup_ahb_status,
        AhbHierarchyMaterialized.segment_ahb_status,
        AhbHierarchyMaterialized.dataelement_ahb_status,
        AhbHierarchyMaterialized.code_ahb_status,
    ]:
        stmt = select(  # type:ignore[call-overload]
            AhbHierarchyMaterialized.edifact_format_version,
            AhbHierarchyMaterialized.format,
            ahb_status_col,
            AhbHierarchyMaterialized.anwendungshandbuch_primary_key,
        )
        rows.extend(session.exec(stmt))
    rows = [r for r in rows if r[2] is not None and r[2].strip()]
    if not any(rows):
        raise ValueError(
            "No rows found in ahb_hierarchy_materialized table; Run `create_db_and_populate_with_ahb_view` before."
        )
    rows.sort(key=lambda x: (x[0], x[1], x[2]))
    seen: set[tuple[str, str, str]] = set()
    unique_rows = [row for row in rows if (key := (row[0], row[1], row[2].strip())) not in seen and not seen.add(key)]
    for row in unique_rows:
        expression = row[2].strip()
        try:
            is_valid, error_message = asyncio.run(is_valid_expression(expression, _content_evaluation_result.set))
            if (
                is_valid
            ):  # we might actually get a meaningful node_texts even for invalid expressions, but I don't like it
                node_texts = _generate_node_texts(session, expression, row.anwendungshandbuch_primary_key)
            else:
                node_texts = ""
        except NotImplementedError:  # ahbicht fault/missing feature -> act like it's valid
            node_texts = _generate_node_texts(session, expression, row.anwendungshandbuch_primary_key)
            error_message = None
        ahb_expression_row = AhbExpression(
            edifact_format_version=row[0],
            format=row[1],
            expression=expression,
            node_texts=node_texts,
            anwendungshandbuch_primary_key=row[3],
            ahbicht_error_message=error_message,
        )
        session.add(ahb_expression_row)
        _logger.debug(
            "Added row (%s, %s, %s) to the ahb_expressions_table",
            ahb_expression_row.edifact_format_version,
            ahb_expression_row.format,
            ahb_expression_row.expression,
        )
    number_of_inserted_rows = session.scalar(
        select(func.count(AhbExpression.id))  # type:ignore[arg-type]# pylint:disable=not-callable
    )
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
            "expression",
            name="idx_ahb_expressions_metadata_expression",
        ),
    )
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    edifact_format_version: EdifactFormatVersion = Field(index=True)
    format: str = Field(index=True)  # the edifact format, e.g. 'UTILMD'
    # expressions and conditions are always interpreted on a per-format basis (no pruefidentifikator required)
    expression: str = Field(index=True)  #: e.g 'Muss [1] U [2]'
    node_texts: str = Field()
    """
    this contains the typical "[1] Foo Text\n[2] Bar Text" which explains the meaning of the nodes from inside the
    respective Expression (e.g. for expression "Muss [1] U [2]")
    """
    ahbicht_error_message: str | None = Field(default=None)
    anwendungshandbuch_primary_key: uuid.UUID = Field()
