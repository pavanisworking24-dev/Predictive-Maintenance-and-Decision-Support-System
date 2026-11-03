
from sqlalchemy import inspect, text

from app.db.session import engine


def inspect_tables():
    """Inspect all database tables and their columns."""

    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())

    print("=" * 80)
    print("DATABASE SCHEMA INSPECTION")
    print("=" * 80)

    print("\nDATABASE TABLES:")
    for table in tables:
        print(f"  - {table}")

    print(f"\nTOTAL TABLES: {len(tables)}")

    for table_name in tables:
        print("\n" + "=" * 80)
        print(f"TABLE: {table_name}")
        print("=" * 80)

        columns = inspector.get_columns(table_name)

        for column in columns:
            print(
                f"  {column['name']}: "
                f"type={column['type']}, "
                f"nullable={column['nullable']}, "
                f"default={column['default']}"
            )


def inspect_embedding_column():
    """Verify the actual PostgreSQL vector column type."""

    print("\n" + "=" * 80)
    print("KNOWLEDGE EMBEDDING COLUMN VERIFICATION")
    print("=" * 80)

    query = text("""
        SELECT
            column_name,
            data_type,
            udt_name,
            is_nullable,
            column_default,
            format_type(a.atttypid, a.atttypmod) AS actual_type
        FROM information_schema.columns c
        JOIN pg_attribute a
            ON a.attname = c.column_name
        JOIN pg_class t
            ON t.oid = a.attrelid
        JOIN pg_namespace n
            ON n.oid = t.relnamespace
        WHERE c.table_schema = 'public'
          AND c.table_name = 'knowledge_chunks'
          AND a.attnum > 0
          AND NOT a.attisdropped
          AND n.nspname = 'public'
          AND t.relname = 'knowledge_chunks'
          AND c.column_name = 'embedding';
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        row = result.fetchone()

        if row is None:
            print("ERROR: embedding column not found.")
            return

        print(f"Column name: {row.column_name}")
        print(f"Data type: {row.data_type}")
        print(f"PostgreSQL internal type: {row.udt_name}")
        print(f"Actual column type: {row.actual_type}")
        print(f"Nullable: {row.is_nullable}")
        print(f"Default: {row.column_default}")

        if row.actual_type == "vector(384)":
            print("\nVECTOR VERIFICATION: SUCCESS")
        else:
            print("\nVECTOR VERIFICATION: CHECK REQUIRED")


def main():
    try:
        inspect_tables()
        inspect_embedding_column()

        print("\n" + "=" * 80)
        print("DATABASE INSPECTION COMPLETED")
        print("=" * 80)

    except Exception as error:
        print("\nDATABASE INSPECTION FAILED")
        print(f"Error: {error}")

        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
