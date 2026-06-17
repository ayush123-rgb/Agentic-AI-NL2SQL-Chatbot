import logging
import sqlite3

from config.config import DATABASE_PATH


logger = logging.getLogger(__name__)

CHAT_HISTORY_TABLE = "chatbot_interactions"
QUERY_MEMORY_TABLE = "query_memory"

INTERNAL_TABLES = {
    CHAT_HISTORY_TABLE,
    QUERY_MEMORY_TABLE
}


def _get_table_columns(conn):
    return {
        row[1]
        for row in conn.execute(
            f"PRAGMA table_info({CHAT_HISTORY_TABLE})"
        )
    }


def _ensure_column(conn, column_name, column_definition):
    columns = _get_table_columns(conn)

    if column_name not in columns:
        conn.execute(
            f"ALTER TABLE {CHAT_HISTORY_TABLE} "
            f"ADD COLUMN {column_name} {column_definition}"
        )


def ensure_chat_history_table(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {CHAT_HISTORY_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            input_question TEXT NOT NULL,
            output TEXT NOT NULL,
            sql_query TEXT NOT NULL,
            context_label TEXT,
            context_source_question TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    _ensure_column(
        conn,
        "context_source_question",
        "TEXT"
    )


def ensure_query_memory_table(conn):
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {QUERY_MEMORY_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_uid TEXT NOT NULL,
            user_input TEXT NOT NULL,
            generated_sql TEXT NOT NULL,
            output_response TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def save_chat_interaction(
    session_id,
    input_question,
    output,
    sql_query,
    context_label=None,
    context_source_question=None
):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:

            ensure_chat_history_table(conn)
            ensure_query_memory_table(conn)

            conn.execute(
                f"""
                INSERT INTO {CHAT_HISTORY_TABLE} (
                    session_id,
                    input_question,
                    output,
                    sql_query,
                    context_label,
                    context_source_question
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    input_question,
                    output,
                    sql_query,
                    context_label,
                    context_source_question
                )
            )

            conn.commit()

    except Exception:
        logger.exception(
            "Failed to save chatbot interaction"
        )


def save_query_memory(
    session_uid,
    user_input,
    generated_sql,
    output_response
):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:

            ensure_query_memory_table(conn)

            conn.execute(
                f"""
                INSERT INTO {QUERY_MEMORY_TABLE}
                (
                    session_uid,
                    user_input,
                    generated_sql,
                    output_response
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    session_uid,
                    user_input,
                    generated_sql,
                    output_response
                )
            )

            conn.commit()

    except Exception:
        logger.exception(
            "Failed to save query memory"
        )


def get_latest_session_context(session_id):
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:

            ensure_chat_history_table(conn)

            return conn.execute(
                f"""
                SELECT
                    context_label,
                    COALESCE(
                        context_source_question,
                        input_question
                    )
                FROM {CHAT_HISTORY_TABLE}
                WHERE session_id = ?
                    AND context_label IS NOT NULL
                ORDER BY id DESC
                LIMIT 1
                """,
                (session_id,)
            ).fetchone()

    except Exception:
        logger.exception(
            "Failed to load latest session context"
        )

    return None