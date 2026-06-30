import logging
import uuid

from fastapi import APIRouter

from app.models import UserQuery

from modules.sql_generator import (
    generate_sql_query
)

from modules.query_validator import (
    validate_sql_query,
    validate_user_query
)

from modules.query_executor import (
    execute_sql_query
)

from modules.response_generator import (
    generate_response
)

from modules.chat_history import (
    save_chat_interaction,
    save_query_memory
)

from modules.semantic_memory import (
    find_similar_query
)

from modules.session_context import (
    needs_context_clarification,
    resolve_session_context
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _context_payload(session_context):
    if not session_context:
        return None

    return session_context.to_response_dict()


def _save_turn(
    session_id,
    user_query,
    output,
    sql_query,
    session_context
):
    context_label = None

    if session_context:
        context_label = session_context.label

    save_chat_interaction(
        session_id=session_id,
        input_question=user_query,
        output=output,
        sql_query=sql_query,
        context_label=context_label,
        context_source_question=(
            session_context.source_question
            if session_context else None
        )
    )


def route_query(user_query, session_id=None):

    logger.info(
        "Received user query: %s",
        user_query
    )

    resolved_session_id, session_context, changed_context = (
        resolve_session_context(
            user_query,
            session_id
        )
    )

    if session_context:
        logger.info(
            "Using session context '%s' for session '%s' (changed=%s)",
            session_context.label,
            resolved_session_id,
            changed_context
        )

    if not validate_user_query(user_query):
        output = "Unsafe database modification request blocked"

        logger.warning(
            "Unsafe user request blocked before SQL generation: %s",
            user_query
        )

        _save_turn(
            resolved_session_id,
            user_query,
            output,
            "NO_SQL_GENERATED_UNSAFE_INTENT",
            session_context
        )

        return {
            "error": output,
            "session_id": resolved_session_id,
            "context": _context_payload(
                session_context
            )
        }

    # ---------------------------------------
    # SEMANTIC MEMORY CHECK
    # ---------------------------------------
    memory_match = None

    try:
        memory_match = find_similar_query(
            user_query
        )
    except Exception:
        logger.exception(
            "Semantic memory lookup failed; continuing without memory"
        )

    if memory_match:

        logger.info(
            "Semantic memory hit with similarity %.2f",
            memory_match["similarity"]
        )

        sql_query = memory_match["sql"]
        memory_hit = True
        similarity = memory_match["similarity"]
    else:
        memory_hit = False
        similarity = None

    if (
        not memory_hit
        and
        not session_context
        and needs_context_clarification(user_query)
    ):
        output = (
            "Please specify the context or table for this question, such as "
            "payments, orders, products, customers, or order items."
        )

        _save_turn(
            resolved_session_id,
            user_query,
            output,
            "NO_SQL_GENERATED_REQUIRES_CONTEXT",
            session_context
        )

        return {
            "message": output,
            "session_id": resolved_session_id,
            "context": None
        }

    if not memory_hit:
        logger.info(
            "STEP 1: Generating SQL query"
        )

        try:
            sql_query = generate_sql_query(
                user_query,
                session_context=session_context
            )
        except Exception:
            logger.exception(
                "SQL generation failed"
            )

            output = "Unable to generate SQL query"

            _save_turn(
                resolved_session_id,
                user_query,
                output,
                "NO_SQL_GENERATED_ERROR",
                session_context
            )

            return {
                "error": output,
                "session_id": resolved_session_id,
                "context": _context_payload(
                    session_context
                )
            }

        logger.info(
            "Generated SQL query: %s",
            sql_query
        )
    else:
        logger.info(
            "Reusing cached SQL query: %s",
            sql_query
        )

    logger.info(
        "STEP 2: Validating SQL query"
    )

    valid = validate_sql_query(
        sql_query
    )

    if not valid:

        logger.warning(
            "Unsafe SQL query blocked: %s",
            sql_query
        )

        output = (
            "Unsafe SQL Query Blocked"
        )

        _save_turn(
            resolved_session_id,
            user_query,
            output,
            sql_query,
            session_context
        )

        return {
            "error": output,
            "session_id": resolved_session_id,
            "context": _context_payload(
                session_context
            )
        }

    logger.info(
        "Query validation successful"
    )

    logger.info(
        "STEP 3: Executing SQL query"
    )

    result = execute_sql_query(
        sql_query
    )

    if isinstance(result, str):

        logger.error(
            "SQL execution failed: %s",
            result
        )

        _save_turn(
            resolved_session_id,
            user_query,
            result,
            sql_query,
            session_context
        )

        return {
            "error": result,
            "session_id": resolved_session_id,
            "context": _context_payload(
                session_context
            )
        }

    if result.empty:

        logger.info(
            "SQL query executed successfully but returned no records"
        )

        output = (
            "No matching records found"
        )

        _save_turn(
            resolved_session_id,
            user_query,
            output,
            sql_query,
            session_context
        )

        return {
            "message": output,
            "session_id": resolved_session_id,
            "context": _context_payload(
                session_context
            )
        }

    logger.info(
        "SQL query returned %s records",
        len(result)
    )

    logger.info(
        "STEP 4: Generating chatbot response"
    )

    try:
        final_response = generate_response(
            user_query,
            sql_query,
            result,
            session_context=session_context
        )
    except Exception:
        logger.exception(
            "Response generation failed"
        )

        final_response = (
            "Query executed successfully. Review the returned data."
        )

    logger.info(
        "Chatbot response generated successfully"
    )

    _save_turn(
        resolved_session_id,
        user_query,
        final_response,
        sql_query,
        session_context
    )

    # ---------------------------------------
    # SAVE TO QUERY MEMORY
    # ---------------------------------------
    if not memory_hit:
        save_query_memory(
            session_uid=resolved_session_id,
            user_input=user_query,
            generated_sql=sql_query,
            output_response=final_response
        )

    return {
        "question": user_query,
        "generated_sql": sql_query,
        "summary": final_response,
        "records_found": len(result),
        "memory_hit": memory_hit,
        "similarity": similarity,
        "session_id": resolved_session_id,
        "context": _context_payload(
            session_context
        ),
        "data": result.head(10).to_dict(
            orient="records"
        )
    }


@router.post("/ask")
def ask_chatbot(user_input: UserQuery):

    return route_query(
        user_input.query,
        session_id=user_input.session_id
    )


@router.post("/create-session")
def create_session():

    session_id = str(
        uuid.uuid4()
    )

    return {
        "session_id": session_id
    }
