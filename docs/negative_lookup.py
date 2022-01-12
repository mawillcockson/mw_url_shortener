from sqlalchemy import (
    Column,
    MetaData,
    String,
    Table,
    alias,
    column,
    create_engine,
    insert,
    join,
    select,
    table,
    text,
    values,
)

potential_short_links = list("abcde")
in_db = ["a"]

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
metadata = MetaData()

short_links_table = Table("short_links", metadata, Column("short_link", String))
temporary_table = Table("temporary", metadata, Column("short_link", String))

metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(
        insert(short_links_table).values(
            {"short_link": short_link for short_link in in_db}
        )
    )
    conn.execute(
        insert(temporary_table).values(
            [{"short_link": short_link} for short_link in potential_short_links]
        )
    )

boring_statement = select(temporary_table.c.short_link).where(
    temporary_table.c.short_link.not_in(select(short_links_table.c.short_link))
)
print(boring_statement)

with engine.begin() as conn:
    print(conn.scalars(boring_statement).all())

statement = text(
    """
SELECT anon_1.temp FROM (
    VALUES (:first), (:second)
) AS anon_1 (temp)
WHERE (
    anon_1.temp NOT IN (
        SELECT short_links.short_link FROM short_links
    )
)
"""
)
print(statement)

with engine.begin() as conn:
    print(conn.scalars(statement, {"first": "a", "second": "b"}).all())
