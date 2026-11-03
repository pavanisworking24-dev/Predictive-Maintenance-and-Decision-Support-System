
from app.db.session import engine
from sqlalchemy import inspect


def main():
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())

    for table in tables:
        print("\n" + "=" * 80)
        print(f"TABLE: {table}")
        print("=" * 80)

        # Primary key
        print("\nPRIMARY KEY:")
        print(inspector.get_pk_constraint(table))

        # Foreign keys
        print("\nFOREIGN KEYS:")
        foreign_keys = inspector.get_foreign_keys(table)

        if not foreign_keys:
            print("  None")

        for fk in foreign_keys:
            print(
                f"  {fk['name']}: "
                f"{fk['constrained_columns']} -> "
                f"{fk['referred_table']}"
                f"{fk['referred_columns']}, "
                f"options={fk.get('options')}"
            )

        # Unique constraints
        print("\nUNIQUE CONSTRAINTS:")
        unique_constraints = inspector.get_unique_constraints(table)

        if not unique_constraints:
            print("  None")

        for constraint in unique_constraints:
            print(
                f"  {constraint['name']}: "
                f"{constraint['column_names']}"
            )

        # Check constraints
        print("\nCHECK CONSTRAINTS:")
        check_constraints = inspector.get_check_constraints(table)

        if not check_constraints:
            print("  None")

        for constraint in check_constraints:
            print(
                f"  {constraint['name']}: "
                f"{constraint['sqltext']}"
            )

        # Indexes
        print("\nINDEXES:")
        indexes = inspector.get_indexes(table)

        if not indexes:
            print("  None")

        for index in indexes:
            print(
                f"  {index['name']}: "
                f"columns={index['column_names']}, "
                f"unique={index['unique']}, "
                f"options={index.get('dialect_options')}"
            )

    engine.dispose()


if __name__ == "__main__":
    main()
