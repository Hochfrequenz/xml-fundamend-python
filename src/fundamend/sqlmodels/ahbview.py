"""
helper module to create a "materialized view" (in sqlite this means: create and populate a plain table)
"""

import logging
from pathlib import Path

import sqlalchemy
from sqlalchemy.orm import Session

_logger = logging.getLogger(__name__)


def create_ahb_view(session: Session) -> None:
    """
    Create a materialized view for the Anwendungshandbücher using a SQLAlchemy session.
    """
    if session.bind.dialect.name != "sqlite":
        _logger.warning("This function is only tested for sqlite")

    sql_path = Path(__file__).parent / "materialize_ahb_view.sql"

    with open(sql_path, "r", encoding="utf-8") as sql_file:
        bare_sql = sql_file.read()

    bare_statements = bare_sql.split(";")

    for bare_statement in bare_statements:
        statement = bare_statement.strip()
        if statement:
            session.execute(sqlalchemy.text(statement))

    session.commit()
