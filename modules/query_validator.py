import re

from modules.chat_history import INTERNAL_TABLES


BLOCKED_SQL_KEYWORDS = (
    "DELETE",
    "DROP",
    "UPDATE",
    "ALTER",
    "INSERT",
    "TRUNCATE",
    "CREATE",
    "REPLACE"
)

DESTRUCTIVE_USER_PATTERNS = (
    r"\b(delete|drop|truncate|alter|insert|update|replace)\b",
    (
        r"\b(remove|erase|destroy)\b.*"
        r"\b(table|database|data|rows?|records?|payments?|orders?|"
        r"products?|customers?|order items?)\b"
    ),
    r"\bcreate\b.*\b(table|database|index)\b"
)


def validate_user_query(user_query):
    normalized_query = str(user_query or "").strip()

    if not normalized_query:
        return False

    return not any(
        re.search(pattern, normalized_query, re.IGNORECASE)
        for pattern in DESTRUCTIVE_USER_PATTERNS
    )


def validate_sql_query(sql_query):
    normalized_query = str(sql_query or "").strip()

    if not normalized_query.upper().startswith("SELECT"):
        return False

    query_without_final_semicolon = normalized_query.rstrip(";")

    if ";" in query_without_final_semicolon:
        return False

    for table_name in INTERNAL_TABLES:
        if re.search(
            rf"\b{re.escape(table_name)}\b",
            normalized_query,
            re.IGNORECASE
        ):
            return False

    for keyword in BLOCKED_SQL_KEYWORDS:
        if re.search(
            rf"\b{keyword}\b",
            normalized_query,
            re.IGNORECASE
        ):
            return False

    return True
