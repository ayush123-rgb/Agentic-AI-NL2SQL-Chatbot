from modules.chat_history import INTERNAL_TABLES


def validate_sql_query(sql_query):
    if not sql_query.strip().upper().startswith("SELECT"):
        return False

    blocked_keywords = [

        "DELETE",
        "DROP",
        "UPDATE",
        "ALTER",
        "INSERT",
        "TRUNCATE",
        "CREATE",
        "REPLACE"

    ]

    sql_upper = sql_query.upper()

    for table_name in INTERNAL_TABLES:
        if table_name.upper() in sql_upper:
            return False

    for keyword in blocked_keywords:

        if keyword in sql_upper:

            return False

    return True
