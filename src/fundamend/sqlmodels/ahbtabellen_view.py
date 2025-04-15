"""
This module contains the SQLModel class for the AHBesser view and a function to create it.
If you never heard about ahbesser, you can safely ignore this module.
https://github.com/Hochfrequenz/ahbesser
"""

import logging
from pathlib import Path
from uuid import UUID

from efoli import EdifactFormat, EdifactFormatVersion
from sqlalchemy.sql.functions import func
from sqlmodel import Field, Session, SQLModel, select

from fundamend.sqlmodels.internals import _execute_bare_sql

_logger = logging.getLogger(__name__)


def create_ahbtabellen_view(session: Session) -> None:
    """
    Create a view for the AHB-Tabellen application: https://github.com/Hochfrequenz/ahbesser
    This assumes that create_db_and_populate_with_ahb_view has already been called.
    If you don't know what ahbesser is, you can safely ignore this function.
    """
    _execute_bare_sql(session=session, path_to_sql_commands=Path(__file__).parent / "create_ahbtabellen_view.sql")
    number_of_rows = session.scalar(
        select(func.count(AhbTabellenLine.id))  # type:ignore[arg-type] # pylint:disable=not-callable
    )
    _logger.info(
        "There are %d rows in the AHBTabellen view %s",
        number_of_rows,
        AhbTabellenLine.__tablename__,
    )


class AhbTabellenLine(SQLModel, table=True):
    """
    Model that represents thew view used by ahbesser. It's created by executing 'create_ahbtabellen_view(session)'
    """

    __tablename__ = "v_ahbtabellen"
    id: UUID = Field(primary_key=True)
    format_version: EdifactFormatVersion = Field()
    format: EdifactFormat = Field()
    pruefidentifikator: str = Field()
    path: str = Field()
    id_path: str = Field()
    direction: str = Field()
    description: str = Field()
    segmentgroup_key: str | None = Field()
    segment_code: str | None = Field()
    data_element: str | None = Field()
    qualifier: str | None = Field()
    line_ahb_status: str | None = Field()
    line_name: str | None = Field()
    bedingung: str | None = Field()
    bedingungsfehler: str | None = Field()
    sort_path: str = Field()


__all__ = ["create_ahbtabellen_view", "AhbTabellenLine"]
