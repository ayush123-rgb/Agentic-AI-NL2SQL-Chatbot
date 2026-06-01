import logging

from fastapi import APIRouter

from app.models import UserQuery
from modules.sql_generator import (
    generate_sql_query
)
from modules.query_validator import (
    validate_sql_query
)
from modules.query_executor import (
    execute_sql_query
)
from modules.response_generator import (
    generate_response
)

router = APIRouter()
logger = logging.getLogger(__name__)


def route_query(user_query):
    logger.info("Received user query: %s", user_query)
    logger.info("STEP 1: Generating SQL query")

    sql_query = generate_sql_query(
        user_query
    )

    logger.info("Generated SQL query: %s", sql_query)
    logger.info("STEP 2: Validating SQL query")

    valid = validate_sql_query(
        sql_query
    )

    if not valid:
        logger.warning("Unsafe SQL query blocked: %s", sql_query)

        return {
            "error": "Unsafe SQL Query Blocked"
        }

    logger.info("Query validation successful")
    logger.info("STEP 3: Executing SQL query")

    result = execute_sql_query(
        sql_query
    )

    if isinstance(result, str):
        logger.error("SQL execution failed: %s", result)

        return {
            "error": result
        }

    if result.empty:
        logger.info("SQL query executed successfully but returned no records")

        return {
            "message": "No matching records found"
        }

    logger.info("SQL query returned %s records", len(result))
    logger.info("STEP 4: Generating chatbot response")

    final_response = generate_response(
        user_query,
        sql_query,
        result
    )

    logger.info("Chatbot response generated successfully")

    return {
        "question": user_query,
        "generated_sql": sql_query,
        "summary": final_response,
        "records_found": len(result),
        "data": result.head(10).to_dict(orient="records")
    }


@router.post("/ask")
def ask_chatbot(user_input: UserQuery):
    return route_query(user_input.query)
