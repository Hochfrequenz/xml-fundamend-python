"""
This module contains the SQLModel class for the AHB diff view and a function to create it.
The view allows comparing two AHB versions to find rows that were added, deleted, or modified.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

import sqlalchemy
from efoli import EdifactFormatVersion
from sqlmodel import Field, Session, SQLModel

from fundamend.sqlmodels.internals import _execute_bare_sql

_logger = logging.getLogger(__name__)


class DiffStatus(str, Enum):
    """Status of a row in the diff view."""

    ADDED = "added"
    DELETED = "deleted"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


def _check_v_ahbtabellen_exists_and_has_data(session: Session) -> None:
    """Check if v_ahbtabellen exists and has data, logging warnings if not."""
    try:
        result = session.execute(sqlalchemy.text("SELECT COUNT(*) FROM v_ahbtabellen"))
        count = result.scalar()
        if count == 0:
            _logger.warning(
                "v_ahbtabellen exists but is empty. "
                "The v_ahb_diff view will not return any results. "
                "Make sure to call create_ahbtabellen_view() after populating the database."
            )
    except sqlalchemy.exc.OperationalError:
        _logger.warning(
            "v_ahbtabellen does not exist. "
            "The v_ahb_diff view requires v_ahbtabellen to be created first. "
            "Call create_ahbtabellen_view() before create_ahb_diff_view()."
        )


def create_ahb_diff_view(session: Session) -> None:
    """
    Create a view for comparing AHB versions.
    This assumes that create_ahb_view (materialize_ahb_view.sql) and
    create_ahbtabellen_view (create_ahbtabellen_view.sql) have already been called.
    """
    _check_v_ahbtabellen_exists_and_has_data(session)
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "create_ahb_diff_view.sql")
    _logger.info("Created view %s", AhbDiffLine.__tablename__)


class AhbDiffLine(SQLModel, table=True):
    """
    Model that represents the diff view for comparing AHB versions.
    This view uses v_ahbtabellen structure and compares line_ahb_status, bedingung, and line_name.

    Query with all 4 filter parameters to compare two specific versions:

        SELECT * FROM v_ahb_diff
        WHERE old_format_version = 'FV2410'
          AND new_format_version = 'FV2504'
          AND old_pruefidentifikator = '55014'
          AND new_pruefidentifikator = '55014'
        ORDER BY sort_path;

    diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
    All value columns exist twice (old_ and new_) to show the values from both versions.
    """

    __tablename__ = "v_ahb_diff"

    # Use a composite key since this is a view joining two tables
    # Note that the triple: (id_path, format_version, pruefidentifikator) is unique, so you can use it to find the
    # matching lines e.g. in v_ahbtabellen by using an inner join and still use ORDER BY sort_path ASC.
    # When building a frontend that compares 2 AWFs in different versions, just make sure that the left and right
    # side of the comparison share the same id_path.
    id_path: str = Field(primary_key=True)
    old_format_version: Optional[EdifactFormatVersion] = Field(primary_key=True, default=None)
    new_format_version: Optional[EdifactFormatVersion] = Field(primary_key=True, default=None)
    old_pruefidentifikator: Optional[str] = Field(primary_key=True, default=None)
    new_pruefidentifikator: Optional[str] = Field(primary_key=True, default=None)

    # Common fields
    sort_path: str = Field()
    path: str = Field()
    line_type: Optional[str] = Field(default=None)

    # Diff status: 'added', 'deleted', 'modified', 'unchanged'
    diff_status: str = Field()

    # Which columns changed (for modified rows only, NULL otherwise)
    # Comma-separated list, e.g. 'line_ahb_status, bedingung'
    changed_columns: Optional[str] = Field(default=None)

    # Old version columns (from v_ahbtabellen)
    old_segmentgroup_key: Optional[str] = Field(default=None)
    old_segment_code: Optional[str] = Field(default=None)
    old_data_element: Optional[str] = Field(default=None)
    old_qualifier: Optional[str] = Field(default=None)
    old_line_ahb_status: Optional[str] = Field(default=None)
    old_line_name: Optional[str] = Field(default=None)
    old_bedingung: Optional[str] = Field(default=None)
    old_bedingungsfehler: Optional[str] = Field(default=None)

    # New version columns (from v_ahbtabellen)
    new_segmentgroup_key: Optional[str] = Field(default=None)
    new_segment_code: Optional[str] = Field(default=None)
    new_data_element: Optional[str] = Field(default=None)
    new_qualifier: Optional[str] = Field(default=None)
    new_line_ahb_status: Optional[str] = Field(default=None)
    new_line_name: Optional[str] = Field(default=None)
    new_bedingung: Optional[str] = Field(default=None)
    new_bedingungsfehler: Optional[str] = Field(default=None)


__all__ = ["create_ahb_diff_view", "AhbDiffLine", "DiffStatus"]
