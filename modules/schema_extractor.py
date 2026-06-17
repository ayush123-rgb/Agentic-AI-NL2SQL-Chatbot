import json
import sqlite3

from config.config import DATABASE_PATH, METADATA_PATH
from modules.chat_history import INTERNAL_TABLES


def load_metadata():
    with METADATA_PATH.open("r", encoding="utf-8") as metadata_file:
        return json.load(metadata_file)


def format_schema_from_metadata(metadata):
    schema_lines = []

    for table in metadata.get("tables", []):
        schema_lines.append(f"TABLE: {table['name']}")
        schema_lines.append(f"Description: {table['description']}")
        schema_lines.append("Columns:")

        for column in table.get("columns", []):
            unit = column.get("unit")
            unit_text = f", unit: {unit}" if unit else ""

            schema_lines.append(
                f"- {column['name']} ({column['type']}): "
                f"{column['description']}{unit_text}"
            )

        sample_data = table.get("sample_data", [])

        if sample_data:
            schema_lines.append("Sample data:")

            for row in sample_data[:3]:
                schema_lines.append(json.dumps(row))

        schema_lines.append("")

    return "\n".join(schema_lines)


def extract_schema_from_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    schema_lines = []

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table';
    """)

    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]

        if table_name in INTERNAL_TABLES:
            continue

        schema_lines.append(f"TABLE: {table_name}")
        schema_lines.append("Columns:")

        cursor.execute(
            f"PRAGMA table_info({table_name})"
        )

        columns = cursor.fetchall()

        for column in columns:
            column_name = column[1]
            column_type = column[2]
            schema_lines.append(f"- {column_name} ({column_type})")

        schema_lines.append("")

    conn.close()

    return "\n".join(schema_lines)


def get_schema():
    if METADATA_PATH.exists():
        return format_schema_from_metadata(load_metadata())

    return extract_schema_from_database()


schema = get_schema()
