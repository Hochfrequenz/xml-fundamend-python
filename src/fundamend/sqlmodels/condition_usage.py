"""
helper module to create a table (and a view) that answers: "where is the AHB condition [931] used?"
This includes use via packages (e.g. [2P]) and UB conditions (e.g. [UB1]), which are resolved transitively.
Like the expression view, this module requires ahbicht and is therefore not imported in fundamend.sqlmodels.__init__.
Import from fundamend.sqlmodels.condition_usage instead.
"""

import asyncio
import logging
import uuid
from collections.abc import Mapping
from enum import StrEnum
from functools import cache

from efoli import EdifactFormat, EdifactFormatVersion
from sqlalchemy import Index, inspect

from fundamend.sqlmodels import AhbHierarchyMaterialized
from fundamend.sqlmodels.anwendungshandbuch import Paket, UbBedingung

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
        Index("idx_ahb_condition_usages_lookup", "edifact_format_version", "format", "condition_key"),
        Index("idx_ahb_condition_usages_ahb_expression", "anwendungshandbuch_primary_key", "expression"),
    )
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    anwendungshandbuch_primary_key: uuid.UUID = Field(foreign_key="anwendungshandbuch.primary_key")
    edifact_format_version: EdifactFormatVersion = Field()
    format: EdifactFormat = Field()  #: the plain edifact format, e.g. 'UTILMD'
    expression: str = Field()  #: stripped expression, e.g. 'Muss [1] U [2]'
    condition_key: str = Field()  #: as returned by ahbicht, without brackets, e.g. '931', '2P', 'UB1'
    key_type: KeyType = Field()
    via: str = Field(default="")  #: '' for direct use, else the outermost package/UB key through which it is used


@cache
def _extract_keys_cached(text: str) -> tuple[tuple[str, KeyType], ...]:
    """parses the text once and returns its keys (deterministically ordered) with their type"""
    extract = asyncio.run(extract_categorized_keys(text))
    result: list[tuple[str, KeyType]] = []
    result.extend(
        (k, KeyType.CONDITION)
        for k in extract.format_constraint_keys + extract.requirement_constraint_keys + extract.hint_keys
    )
    result.extend((k, KeyType.PACKAGE) for k in extract.package_keys)
    result.extend((k, KeyType.UB_CONDITION) for k in extract.time_condition_keys)
    return tuple(result)


def resolve_condition_keys(expression: str, definitions: Mapping[str, str]) -> list[tuple[str, KeyType, str]]:
    """
    Returns the sorted, distinct (condition_key, key_type, via) tuples of the expression.
    `definitions` maps the package/UB keys of one AHB to their definition texts.
    Direct use has via=''; keys that are reached through a package/UB condition get the outermost such key as via.
    Raises the parser's exception if the expression cannot be parsed.
    """
    result: set[tuple[str, KeyType, str]] = set()
    top_level = _extract_keys_cached(expression)
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
            try:
                children = _extract_keys_cached(definition)
            except Exception as error:  # pylint:disable=broad-exception-caught
                # e.g. '--' for packages that are not further defined; the parser raises different exception types
                _logger.info("The definition of '%s' could not be parsed: %s", current, error)
                continue
            for child_key, child_type in children:
                if child_key in visited:
                    continue
                visited.add(child_key)
                result.add((child_key, child_type, root_key))
                if child_type != KeyType.CONDITION:
                    stack.append(child_key)
    return sorted(result, key=lambda r: (r[0], r[1].value, r[2]))


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
            if version is not None and status is not None and status.strip() and ahb_pk is not None:
                rows.add((EdifactFormatVersion(version), str(edifact_format), status.strip(), ahb_pk))
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
    # sorted by stable columns; the AHB primary key is a random uuid and is only the last tie breaker
    for version, edifact_format, expression, ahb_pk in sorted(rows, key=lambda r: (r[0], r[1], r[2], str(r[3]))):
        try:
            resolved = resolve_condition_keys(expression, definitions_by_ahb.get(ahb_pk, {}))
        except Exception as error:  # pylint:disable=broad-exception-caught
            _logger.info("The expression '%s' could not be parsed: %s", expression, error)
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
    AhbConditionUsage.__table__.create(session.get_bind(), checkfirst=True)  # type: ignore[attr-defined]
    session.exec(delete(AhbConditionUsage))  # makes the function idempotent
    session.add_all(usages)
    session.commit()
    _logger.info("Inserted %d rows into the table %s", len(usages), AhbConditionUsage.__tablename__)
