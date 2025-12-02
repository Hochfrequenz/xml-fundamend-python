"""
This module contains the SQLModel class for the AHB diff view and a function to create it.
The view allows comparing two AHB versions to find rows that were added, deleted, or modified.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional

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


def create_ahb_diff_view(session: Session) -> None:
    """
    Create a view for comparing AHB versions.
    This assumes that create_ahb_view (materialize_ahb_view.sql) has already been called.
    """
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "create_ahb_diff_view.sql")
    _logger.info("Created view %s", AhbDiffLine.__tablename__)


class AhbDiffLine(SQLModel, table=True):
    """
    Model that represents the diff view for comparing AHB versions.
    Query with all 4 parameters to compare two specific versions:

        SELECT * FROM v_ahb_diff
        WHERE format_version_a = 'FV2504'
          AND format_version_b = 'FV2410'
          AND pruefidentifikator_a = '55014'
          AND pruefidentifikator_b = '55014'
          AND diff_status = 'added'
        ORDER BY sort_path;

    diff_status can be: 'added', 'deleted', 'modified', 'unchanged'
    All value columns exist twice (_a and _b) to show the values from both versions.
    """

    __tablename__ = "v_ahb_diff"

    # Use a composite key since this is a view joining two tables
    # Note that the triple: (id_path, format_version, prüfidentifikator) is unique, so you can use it to find the
    # matching lines e.g. in v_ahbtabellen by using an inner joins and still use ORDER BY sort_path ASC.
    # When building a frontend that compares 2 AWFs in different versions, just make sure that the left and right
    # side of the comparison share the same id_path.
    id_path: str = Field(primary_key=True)
    format_version_a: Optional[EdifactFormatVersion] = Field(primary_key=True)
    format_version_b: Optional[EdifactFormatVersion] = Field(primary_key=True)
    pruefidentifikator_a: Optional[str] = Field(primary_key=True)
    pruefidentifikator_b: Optional[str] = Field(primary_key=True)

    path: str = Field()
    sort_path: str = Field()
    type: str = Field()

    # Segment Group (both versions)
    segmentgroup_name_a: Optional[str] = Field(default=None)
    segmentgroup_name_b: Optional[str] = Field(default=None)
    segmentgroup_ahb_status_a: Optional[str] = Field(default=None)
    segmentgroup_ahb_status_b: Optional[str] = Field(default=None)

    # Segment (both versions)
    segment_id_a: Optional[str] = Field(default=None)
    segment_id_b: Optional[str] = Field(default=None)
    segment_name_a: Optional[str] = Field(default=None)
    segment_name_b: Optional[str] = Field(default=None)
    segment_ahb_status_a: Optional[str] = Field(default=None)
    segment_ahb_status_b: Optional[str] = Field(default=None)

    # Data Element Group (both versions)
    dataelementgroup_id_a: Optional[str] = Field(default=None)
    dataelementgroup_id_b: Optional[str] = Field(default=None)
    dataelementgroup_name_a: Optional[str] = Field(default=None)
    dataelementgroup_name_b: Optional[str] = Field(default=None)

    # Data Element (both versions)
    dataelement_id_a: Optional[str] = Field(default=None)
    dataelement_id_b: Optional[str] = Field(default=None)
    dataelement_name_a: Optional[str] = Field(default=None)
    dataelement_name_b: Optional[str] = Field(default=None)
    dataelement_ahb_status_a: Optional[str] = Field(default=None)
    dataelement_ahb_status_b: Optional[str] = Field(default=None)

    # Code (both versions)
    code_value_a: Optional[str] = Field(default=None)
    code_value_b: Optional[str] = Field(default=None)
    code_name_a: Optional[str] = Field(default=None)
    code_name_b: Optional[str] = Field(default=None)
    code_ahb_status_a: Optional[str] = Field(default=None)
    code_ahb_status_b: Optional[str] = Field(default=None)

    # Diff status: 'added', 'deleted', 'modified', 'unchanged'
    diff_status: str = Field()


__all__ = ["create_ahb_diff_view", "AhbDiffLine", "DiffStatus"]
