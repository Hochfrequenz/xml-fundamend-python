"""
helper module to create a table (and a view) that answers: "where is the AHB condition [931] used?"
This includes use via packages (e.g. [2P]) and UB conditions (e.g. [UB1]), which are resolved transitively.
Like the expression view, this module requires ahbicht and is therefore not imported in fundamend.sqlmodels.__init__.
Import from fundamend.sqlmodels.condition_usage instead.
"""

import asyncio
import logging
import threading
import uuid
from collections.abc import Mapping
from enum import StrEnum
from functools import cache
from pathlib import Path

from efoli import EdifactFormat, EdifactFormatVersion
from sqlalchemy import Enum, Index, inspect, text

from fundamend.sqlmodels import AhbHierarchyMaterialized
from fundamend.sqlmodels.anwendungshandbuch import Paket, UbBedingung
from fundamend.sqlmodels.internals import _execute_bare_sql

try:
    from sqlmodel import Field, Session, SQLModel, UniqueConstraint, delete, select

except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    raise

try:
    from ahbicht.expressions.condition_expression_parser import extract_categorized_keys
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels,ahbicht]?"
    raise

_logger = logging.getLogger(__name__)


class KeyType(StrEnum):
    """the kind of key that is used in an expression"""

    CONDITION = "condition"  #: plain condition, e.g. 931 (also hints and format constraints)
    PACKAGE = "package"  #: Bedingungspaket, e.g. 2P
    UB_CONDITION = "ub_condition"  #: UB-Bedingung, e.g. UB1


# by default, sqlalchemy stores the names (CONDITION) of enums; SQL consumers should see the values (condition)
_KEY_TYPE_COLUMN = Enum(
    KeyType, values_callable=lambda enum_class: [member.value for member in enum_class], native_enum=False
)


class AhbConditionUsage(SQLModel, table=True):
    """
    One row per (AHB, expression, condition key, via). 'via' is the empty string for direct use and the key of the
    outermost package/UB condition if the key is only used indirectly.
    """

    __tablename__ = "ahb_condition_usages"
    __table_args__ = (
        UniqueConstraint(
            "anwendungshandbuch_primary_key",
            "expression",
            "condition_key",
            "via",
            name="idx_ahb_condition_usages_unique",
        ),
        # format is optional in the lookups, hence it comes after condition_key
        Index("idx_ahb_condition_usages_lookup", "edifact_format_version", "condition_key", "format"),
        Index("idx_ahb_condition_usages_ahb_expression", "anwendungshandbuch_primary_key", "expression"),
    )
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    anwendungshandbuch_primary_key: uuid.UUID = Field(foreign_key="anwendungshandbuch.primary_key")
    edifact_format_version: EdifactFormatVersion = Field()
    format: EdifactFormat = Field()  #: the plain edifact format, e.g. 'UTILMD'
    expression: str = Field()  #: stripped expression, e.g. 'Muss [1] U [2]'
    condition_key: str = Field()  #: as returned by ahbicht, without brackets, e.g. '931', '2P', 'UB1'
    key_type: KeyType = Field(sa_type=_KEY_TYPE_COLUMN)  # stored as 'condition', 'package', 'ub_condition'
    via: str = Field(default="")  #: '' for direct use, else the outermost package/UB key through which it is used


def _parse_keys(text: str) -> tuple[tuple[str, KeyType], ...]:
    """parses the text (uncached) and returns its keys (deterministically ordered) with their type"""
    extract = asyncio.run(extract_categorized_keys(text))
    result: list[tuple[str, KeyType]] = []
    result.extend(
        (k, KeyType.CONDITION)
        for k in extract.format_constraint_keys + extract.requirement_constraint_keys + extract.hint_keys
    )
    result.extend((k, KeyType.PACKAGE) for k in extract.package_keys)
    result.extend((k, KeyType.UB_CONDITION) for k in extract.time_condition_keys)
    return tuple(result)


@cache
def _extract_keys_cached(text: str) -> tuple[tuple[str, KeyType], ...] | None:
    """
    Parses each distinct text exactly once. Returns None if the text cannot be parsed (e.g. '--'); failures are cached
    too (functools.cache would not store exceptions) and logged once.
    """
    try:
        return _parse_keys(text)
    except Exception as error:  # pylint:disable=broad-exception-caught
        # the parser raises different exception types (SyntaxError, lark errors, ...); '--' is a common definition
        _logger.info("The text '%s' could not be parsed: %s", text, error)
        return None


def resolve_condition_keys(expression: str, definitions: Mapping[str, str]) -> list[tuple[str, KeyType, str]]:
    """
    Returns the sorted, distinct (condition_key, key_type, via) tuples of the expression.
    `definitions` maps the package/UB keys of one AHB to their definition texts.
    Direct use has via=''; keys that are reached through a package/UB condition get the outermost such key as via.
    Raises a ValueError if the expression cannot be parsed.
    """
    result: set[tuple[str, KeyType, str]] = set()
    top_level = _extract_keys_cached(expression)
    if top_level is None:
        raise ValueError(f"The expression '{expression}' could not be parsed.")
    for key, key_type in top_level:
        result.add((key, key_type, ""))
    for root_key, root_type in top_level:
        if root_type == KeyType.CONDITION:
            continue
        visited = {root_key}
        stack = [root_key]
        while stack:
            current = stack.pop()
            definition = definitions.get(current)
            if definition is None:
                _logger.info("There is no definition for the key '%s'", current)
                continue
            children = _extract_keys_cached(definition)
            if children is None:  # e.g. '--' for packages that are not further defined
                continue
            for child_key, child_type in children:
                if child_key in visited:
                    continue
                visited.add(child_key)
                result.add((child_key, child_type, root_key))
                if child_type != KeyType.CONDITION:
                    stack.append(child_key)
    return sorted(result, key=lambda r: (r[0], r[1].value, r[2]))


class _CurrentThreadFilter(logging.Filter):
    """drops all log records that were emitted by the thread that created the filter"""

    def __init__(self) -> None:
        super().__init__()
        self._thread_id = threading.get_ident()

    def filter(self, record: logging.LogRecord) -> bool:
        return record.thread != self._thread_id


def create_and_fill_ahb_condition_usage_table(session: Session) -> None:
    """
    creates and fills the ahb_condition_usages table from ahb_hierarchy_materialized.
    Requires that the AHB was built with drop_raw_tables=False (needs the paket and ubbedingung tables; with
    drop_raw_tables=True the anwendungshandbuch table, the target of the foreign key, is missing, too).
    """
    table_names = set(inspect(session.get_bind()).get_table_names())
    missing = {"anwendungshandbuch", "paket", "ubbedingung"} - table_names
    if missing:
        raise ValueError(
            f"The tables {sorted(missing)} are missing. Build the database with drop_raw_tables=False "
            "(create_db_and_populate_with_ahb_view)."
        )
    _extract_keys_cached.cache_clear()  # failures are cached, too; don't let an earlier transient one stick
    rows: set[tuple[EdifactFormatVersion, str, str, uuid.UUID]] = set()  # (version, format, expression, ahb pk)
    for ahb_status_col in [
        AhbHierarchyMaterialized.segmentgroup_ahb_status,
        AhbHierarchyMaterialized.segment_ahb_status,
        AhbHierarchyMaterialized.dataelement_ahb_status,
        AhbHierarchyMaterialized.code_ahb_status,
    ]:
        stmt = select(
            AhbHierarchyMaterialized.edifact_format_version,
            AhbHierarchyMaterialized.format,
            ahb_status_col,
            AhbHierarchyMaterialized.anwendungshandbuch_primary_key,
        ).distinct()
        for version, edifact_format, status, ahb_pk in session.exec(stmt):
            if version is not None and status is not None and status.strip(" ") and ahb_pk is not None:
                rows.add((EdifactFormatVersion(version), str(edifact_format), status.strip(" "), ahb_pk))
    if not rows:
        raise ValueError(
            "No rows found in ahb_hierarchy_materialized table; Run `create_db_and_populate_with_ahb_view` before."
        )
    definitions_by_ahb: dict[uuid.UUID, dict[str, str]] = {}
    for paket in session.exec(select(Paket)).all():
        if paket.anwendungshandbuch_primary_key is not None:
            definitions_by_ahb.setdefault(paket.anwendungshandbuch_primary_key, {})[paket.nummer] = paket.text
    for ub_bedingung in session.exec(select(UbBedingung)).all():
        if ub_bedingung.anwendungshandbuch_primary_key is not None:
            definitions_by_ahb.setdefault(ub_bedingung.anwendungshandbuch_primary_key, {})[ub_bedingung.nummer] = (
                ub_bedingung.text
            )
    usages: list[AhbConditionUsage] = []
    skipped = 0
    # ahbicht logs warnings with tracebacks for every unparsable text like '--' (its parsing logger sets own level);
    # drop those records, but only the ones of this thread, so other threads' logging stays untouched
    log_filter = _CurrentThreadFilter()
    ahbicht_loggers = [logging.getLogger(name) for name in ("ahbicht", "ahbicht.expressions")]
    for ahbicht_logger in ahbicht_loggers:
        ahbicht_logger.addFilter(log_filter)
    try:
        # sorted by stable columns; the AHB primary key is a random uuid and is only the last tie breaker
        for version, edifact_format, expression, ahb_pk in sorted(rows, key=lambda r: (r[0], r[1], r[2], str(r[3]))):
            try:
                resolved = resolve_condition_keys(expression, definitions_by_ahb.get(ahb_pk, {}))
            except ValueError as error:
                _logger.warning("Skipping the expression '%s': %s", expression, error)
                skipped += 1
                continue
            usages.extend(
                AhbConditionUsage(
                    anwendungshandbuch_primary_key=ahb_pk,
                    edifact_format_version=version,
                    format=EdifactFormat(edifact_format),
                    expression=expression,
                    condition_key=key,
                    key_type=key_type,
                    via=via,
                )
                for key, key_type, via in resolved
            )
    finally:
        for ahbicht_logger in ahbicht_loggers:
            ahbicht_logger.removeFilter(log_filter)
    if skipped == len(rows):
        raise ValueError(f"None of the {skipped} expressions could be parsed; the table was not filled.")
    AhbConditionUsage.__table__.create(session.get_bind(), checkfirst=True)  # type: ignore[attr-defined]
    session.exec(delete(AhbConditionUsage))  # makes the function idempotent
    session.add_all(usages)
    session.commit()
    _logger.info("Inserted %d rows into the table %s", len(usages), AhbConditionUsage.__tablename__)


def create_ahb_condition_usage_view(session: Session) -> None:
    """
    Creates the view v_ahb_condition_usages: one row per AHB line (v_ahbtabellen) and condition key that the line uses,
    directly (via is NULL) or through a package/UB condition (via is the outermost package/UB key).
    Requires v_ahbtabellen (create_ahbtabellen_view) and ahb_condition_usages
    (create_and_fill_ahb_condition_usage_table).
    """
    inspector = inspect(session.get_bind())
    if "v_ahbtabellen" not in inspector.get_view_names():
        raise ValueError("The view v_ahbtabellen is missing. Call create_ahbtabellen_view before.")
    if (
        AhbConditionUsage.__tablename__ not in inspector.get_table_names()
        or session.exec(select(AhbConditionUsage.id).limit(1)).first() is None
    ):
        raise ValueError(
            f"The table {AhbConditionUsage.__tablename__} is missing or empty. "
            "Call create_and_fill_ahb_condition_usage_table before."
        )
    # the view joins ahb_hierarchy_materialized on (anwendungshandbuch_primary_key, line_ahb_status); without this index
    # sqlite uses idx_line_ahb_status alone, which matches the rows of _all_ AHBs for common expressions like 'X'
    session.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_ahm_ahb_pk_line_ahb_status "
            "ON ahb_hierarchy_materialized (anwendungshandbuch_primary_key, line_ahb_status)"
        )
    )
    _execute_bare_sql(
        session=session, path_to_sql_commands=Path(__file__).parent / "create_ahb_condition_usage_view.sql"
    )


class AhbConditionUsageLine(SQLModel, table=True):
    """
    Read model for the view v_ahb_condition_usages. It's created by executing 'create_ahb_condition_usage_view(session)'
    """

    __tablename__ = "v_ahb_condition_usages"
    id: str = Field(primary_key=True)  #: v_ahbtabellen id and usage id concatenated
    format_version: EdifactFormatVersion = Field()
    format: EdifactFormat = Field()
    pruefidentifikator: str = Field()
    description: str = Field()
    direction: str = Field()
    segmentgroup_key: str | None = Field()
    segment_code: str | None = Field()
    data_element: str | None = Field()
    qualifier: str | None = Field()
    line_name: str | None = Field()
    line_ahb_status: str | None = Field()
    sort_path: str = Field()
    anwendungshandbuch_primary_key: uuid.UUID = Field()
    condition_key: str = Field()
    key_type: KeyType = Field(sa_type=_KEY_TYPE_COLUMN)
    via: str | None = Field()  #: None for direct use
