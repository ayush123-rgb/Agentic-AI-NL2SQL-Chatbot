import logging
import sqlite3
import time

import pandas as pd

from config.config import DATABASE_PATH

logger = logging.getLogger(__name__)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def execute_sql_query(sql_query):
    try:
        logger.info("Executing SQL query against database: %s", DATABASE_PATH)
        logger.info("SQL query: %s", sql_query)

        conn = sqlite3.connect(DATABASE_PATH)

        start_time = time.time()

        result = pd.read_sql_query(sql_query, conn)

        end_time = time.time()

        execution_time = end_time - start_time

        logger.info(
            "Query execution time: %.4f seconds",
            execution_time
        )

        conn.close()

        return result

    except Exception as e:
        logger.exception("SQL execution error")

        return str(e)
