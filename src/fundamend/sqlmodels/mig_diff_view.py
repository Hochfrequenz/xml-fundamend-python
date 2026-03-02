"""
This module contains the SQLModel class for the MIG diff view and a function to create it.
The view allows comparing two MIG versions to find rows that were added, deleted, or modified.
"""

# pylint: disable=duplicate-code
# This module intentionally follows the same patterns as ahb_diff_view.py

import logging
from pathlib import Path
from typing import Optional

import sqlalchemy
from efoli import EdifactFormat, EdifactFormatVersion
from sqlmodel import Field, Session, SQLModel

from fundamend.sqlmodels.internals import _execute_bare_sql

_logger = logging.getLogger(__name__)


def _check_mig_hierarchy_exists_and_has_data(session: Session) -> None:
    """Check if mig_hierarchy_materialized exists and has data, logging warnings if not."""
    try:
        result = session.execute(sqlalchemy.text("SELECT COUNT(*) FROM mig_hierarchy_materialized"))
        count = result.scalar()
        if count == 0:
            _logger.warning(
                "mig_hierarchy_materialized exists but is empty. "
                "The v_mig_diff view will not return any results. "
                "Make sure to call create_mig_view() after populating the database."
            )
    except sqlalchemy.exc.OperationalError:
        _logger.warning(
            "mig_hierarchy_materialized does not exist. "
            "The v_mig_diff view requires mig_hierarchy_materialized to be created first. "
            "Call create_mig_view() before create_mig_diff_view()."
        )


def create_mig_diff_view(session: Session) -> None:
    """
    Create a view for comparing MIG versions.
    This assumes that create_mig_view (materialize_mig_view.sql) has already been called.
    """
    _check_mig_hierarchy_exists_and_has_data(session)
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "create_mig_diff_view.sql")
    _logger.info("Created view %s", MigDiffLine.__tablename__)


class MigDiffLine(SQLModel, table=True):
    """
    Model that represents the diff view for comparing MIG versions.
    This view uses mig_hierarchy_materialized structure and compares line_status_std,
    line_status_specification, and line_name.

    Query with all 4 filter parameters to compare two specific versions:

        SELECT * FROM v_mig_diff
        WHERE old_format_version = 'FV2410'
          AND new_format_version = 'FV2504'
          AND old_format = 'UTILTS'
          AND new_format = 'UTILTS'
        ORDER BY sort_path;

    diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
    All value columns exist twice (old_ and new_) to show the values from both versions.

    MATCHING STRATEGY:
    Unlike AHBs (which have Prüfidentifikatoren as stable semantic anchors), MIGs represent
    the complete message structure without such anchors. This view matches rows by their
    human-readable 'path' column (e.g., "Nachrichten-Kopfsegment > Nachrichten-Kennung > ...")
    rather than structural id_path. This provides more semantically meaningful comparisons
    but has limitations:
    - If an element is renamed between versions, it appears as added+deleted rather than modified
    - Elements with identical names at different structural positions may be incorrectly matched
    For structural comparisons, use id_path directly from mig_hierarchy_materialized.
    """

    __tablename__ = "v_mig_diff"

    # Composite primary key
    id_path: str = Field(primary_key=True)
    old_format_version: Optional[EdifactFormatVersion] = Field(primary_key=True, default=None)
    new_format_version: Optional[EdifactFormatVersion] = Field(primary_key=True, default=None)
    old_format: Optional[EdifactFormat] = Field(primary_key=True, default=None)
    new_format: Optional[EdifactFormat] = Field(primary_key=True, default=None)

    # Common fields
    sort_path: str = Field()
    path: str = Field()
    line_type: Optional[str] = Field(default=None)

    # Diff status: 'added', 'deleted', 'modified', 'unchanged'
    diff_status: str = Field()

    # Which columns changed (for modified rows only, NULL otherwise)
    changed_columns: Optional[str] = Field(default=None)

    # Old version columns
    old_segmentgroup_id: Optional[str] = Field(default=None)
    old_segment_id: Optional[str] = Field(default=None)
    old_dataelement_id: Optional[str] = Field(default=None)
    old_code_value: Optional[str] = Field(default=None)
    old_line_status_std: Optional[str] = Field(default=None)
    old_line_status_specification: Optional[str] = Field(default=None)
    old_line_name: Optional[str] = Field(default=None)

    # New version columns
    new_segmentgroup_id: Optional[str] = Field(default=None)
    new_segment_id: Optional[str] = Field(default=None)
    new_dataelement_id: Optional[str] = Field(default=None)
    new_code_value: Optional[str] = Field(default=None)
    new_line_status_std: Optional[str] = Field(default=None)
    new_line_status_specification: Optional[str] = Field(default=None)
    new_line_name: Optional[str] = Field(default=None)


__all__ = ["create_mig_diff_view", "MigDiffLine"]
