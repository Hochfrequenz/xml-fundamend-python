"""internal helper functions"""

from pathlib import Path

try:
    import sqlalchemy
    from sqlmodel import Session
except ImportError as import_error:
    import_error.msg += "; Did you install fundamend[sqlmodels] or did you try to import from fundamend.models instead?"
    # sqlmodel is only an optional dependency when fundamend is used to fill a database
    raise


def _execute_bare_sql(session: Session, path_to_sql_commands: Path) -> None:
    """
    Execute bare SQL from the path_to_sqlcommands in the given SQLAlchemy session.
    """

    with open(path_to_sql_commands, "r", encoding="utf-8") as sql_file:
        bare_sql = sql_file.read()

    bare_statements = bare_sql.split(";")

    for bare_statement in bare_statements:
        statement = bare_statement.strip()
        if statement:
            try:
                session.execute(sqlalchemy.text(statement))
            except sqlalchemy.exc.IntegrityError:
                if " UNIQUE " in bare_statement:
                    session.execute(sqlalchemy.text(bare_statement.replace(" UNIQUE ", " ")))
                else:
                    raise
    session.commit()
