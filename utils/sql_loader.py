from pathlib import Path


SQL_ROOT = (
    Path(__file__)
    .parent.parent
     
)


def load_sql(
    relative_path: str
) -> str:

    sql_file = (
        SQL_ROOT
        / relative_path
    )

    return sql_file.read_text(
        encoding="utf-8"
    )