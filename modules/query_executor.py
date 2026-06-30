import logging
import sqlite3
import time

import pandas as pd

from config.config import DATABASE_PATH

logger = logging.getLogger(__name__)
MAX_RESULT_ROWS = 1000

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def _limited_sql_query(sql_query, max_rows):
    normalized_query = sql_query.strip().rstrip(";")

    return (
        "SELECT * FROM ("
        f"{normalized_query}"
        ") AS limited_query_result "
        f"LIMIT {int(max_rows)}"
    )


def execute_sql_query(sql_query, max_rows=MAX_RESULT_ROWS):
    try:
        logger.info("Executing SQL query against database: %s", DATABASE_PATH)
        logger.info("SQL query: %s", sql_query)
        logger.info("Maximum rows returned: %s", max_rows)

        execution_query = _limited_sql_query(
            sql_query,
            max_rows
        )

        with sqlite3.connect(DATABASE_PATH) as conn:
            start_time = time.time()

            result = pd.read_sql_query(
                execution_query,
                conn
            )

            end_time = time.time()

        execution_time = end_time - start_time

        logger.info(
            "Query execution time: %.4f seconds",
            execution_time
        )

        return result

    except Exception as e:
        logger.exception("SQL execution error")

        return str(e)
