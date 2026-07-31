"""
This module contains the SQLModel class for the AHB pruefi diff view and a function to create it.
The view allows comparing two DIFFERENT Pruefidentifikatoren within the SAME AHB format version to find
rows that were added, deleted, or modified.
For comparing the SAME Pruefidentifikator across two format versions, see ahb_formatversion_diff_view.py.
"""

# pylint: disable=duplicate-code
# This module intentionally follows the same patterns as ahb_formatversion_diff_view.py

import logging
from pathlib import Path

import sqlalchemy
from efoli import EdifactFormatVersion
from sqlmodel import Field, Session, SQLModel

from fundamend.sqlmodels.internals import _execute_bare_sql

_logger = logging.getLogger(__name__)


def _check_v_ahbtabellen_exists_and_has_data(session: Session) -> None:
    """Check if v_ahbtabellen exists and has data, logging warnings if not."""
    try:
        result = session.execute(sqlalchemy.text("SELECT COUNT(*) FROM v_ahbtabellen"))
        count = result.scalar()
        if count == 0:
            _logger.warning(
                "v_ahbtabellen exists but is empty. "
                "The v_ahb_pruefi_diff view will not return any results. "
                "Make sure to call create_ahbtabellen_view() after populating the database."
            )
    except sqlalchemy.exc.OperationalError:
        _logger.warning(
            "v_ahbtabellen does not exist. "
            "The v_ahb_pruefi_diff view requires v_ahbtabellen to be created first. "
            "Call create_ahbtabellen_view() before create_ahb_pruefi_diff_view()."
        )


def create_ahb_pruefi_diff_view(session: Session) -> None:
    """
    Create a view for comparing two different Pruefidentifikatoren within the same AHB format version.
    This assumes that create_ahb_view (materialize_ahb_view.sql) and
    create_ahbtabellen_view (create_ahbtabellen_view.sql) have already been called.
    """
    _check_v_ahbtabellen_exists_and_has_data(session)
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "create_ahb_pruefi_diff_view.sql")
    _logger.info("Created view %s", AhbPruefiDiffLine.__tablename__)


class AhbPruefiDiffLine(SQLModel, table=True):
    """
    Model that represents the diff view for comparing two different Pruefidentifikatoren within the
    same AHB format version.
    This view uses v_ahbtabellen structure and compares line_ahb_status, bedingung, and line_name.

    Query with all 3 filter parameters to compare two specific pruefidentifikatoren:

        SELECT * FROM v_ahb_pruefi_diff
        WHERE old_format_version = 'FV2504'
          AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55014'
          AND new_pruefidentifikator = '55024'
        ORDER BY sort_path;

    diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
    All value columns exist twice (old_ and new_) to show the values for both pruefidentifikatoren.
    """

    __tablename__ = "v_ahb_pruefi_diff"

    # Use a composite key since this is a view joining two tables
    # Note that the triple: (id_path, format_version, pruefidentifikator) is unique, so you can use it to find the
    # matching lines e.g. in v_ahbtabellen by using an inner join and still use ORDER BY sort_path ASC.
    # When building a frontend that compares 2 AWFs within the same format version, just make sure that the left and
    # right side of the comparison share the same id_path.
    id_path: str = Field(primary_key=True)
    old_format_version: EdifactFormatVersion | None = Field(primary_key=True, default=None)
    new_format_version: EdifactFormatVersion | None = Field(primary_key=True, default=None)
    old_pruefidentifikator: str | None = Field(primary_key=True, default=None)
    new_pruefidentifikator: str | None = Field(primary_key=True, default=None)

    # Common fields
    sort_path: str = Field()
    path: str = Field()
    line_type: str | None = Field(default=None)

    # Diff status: 'added', 'deleted', 'modified', 'unchanged'
    diff_status: str = Field()

    # Which columns changed (for modified rows only, NULL otherwise)
    # Comma-separated list, e.g. 'line_ahb_status, bedingung'
    changed_columns: str | None = Field(default=None)

    # Old pruefidentifikator columns (from v_ahbtabellen)
    old_segmentgroup_key: str | None = Field(default=None)
    old_segment_code: str | None = Field(default=None)
    old_data_element: str | None = Field(default=None)
    old_qualifier: str | None = Field(default=None)
    old_line_ahb_status: str | None = Field(default=None)
    old_line_name: str | None = Field(default=None)
    old_bedingung: str | None = Field(default=None)
    old_bedingungsfehler: str | None = Field(default=None)

    # New pruefidentifikator columns (from v_ahbtabellen)
    new_segmentgroup_key: str | None = Field(default=None)
    new_segment_code: str | None = Field(default=None)
    new_data_element: str | None = Field(default=None)
    new_qualifier: str | None = Field(default=None)
    new_line_ahb_status: str | None = Field(default=None)
    new_line_name: str | None = Field(default=None)
    new_bedingung: str | None = Field(default=None)
    new_bedingungsfehler: str | None = Field(default=None)


__all__ = ["AhbPruefiDiffLine", "create_ahb_pruefi_diff_view"]
