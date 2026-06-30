import unittest
from unittest.mock import patch

import pandas as pd

import app.router as router_module
from modules.query_executor import execute_sql_query
from modules.query_validator import (
    validate_sql_query,
    validate_user_query
)


class QueryValidationTests(unittest.TestCase):
    def test_destructive_user_request_is_blocked(self):
        self.assertFalse(
            validate_user_query("delete payments table")
        )

    def test_safe_read_request_is_allowed(self):
        self.assertTrue(
            validate_user_query("show payment values")
        )

    def test_multiple_sql_statements_are_blocked(self):
        self.assertFalse(
            validate_sql_query(
                "SELECT * FROM payments; SELECT * FROM orders"
            )
        )


class RouterWorkflowTests(unittest.TestCase):
    @patch.object(router_module, "_save_turn")
    @patch.object(router_module, "generate_sql_query")
    @patch.object(router_module, "find_similar_query")
    @patch.object(router_module, "resolve_session_context")
    def test_destructive_request_stops_before_memory_and_generation(
        self,
        resolve_context,
        find_memory,
        generate_sql,
        save_turn
    ):
        resolve_context.return_value = (
            "test-session",
            None,
            False
        )

        response = router_module.route_query(
            "delete payments table",
            "test-session"
        )

        self.assertIn("error", response)
        find_memory.assert_not_called()
        generate_sql.assert_not_called()
        save_turn.assert_called_once()

    @patch.object(router_module, "save_query_memory")
    @patch.object(router_module, "_save_turn")
    @patch.object(router_module, "generate_response")
    @patch.object(router_module, "execute_sql_query")
    @patch.object(router_module, "find_similar_query")
    @patch.object(router_module, "resolve_session_context")
    def test_memory_hit_executes_cached_sql_and_returns_rows(
        self,
        resolve_context,
        find_memory,
        execute_sql,
        generate_response,
        save_turn,
        save_memory
    ):
        resolve_context.return_value = (
            "test-session",
            None,
            False
        )
        find_memory.return_value = {
            "sql": "SELECT payment_value FROM payments LIMIT 2",
            "response": "old cached response",
            "similarity": 0.99
        }
        execute_sql.return_value = pd.DataFrame(
            {"payment_value": [100.0, 200.0]}
        )
        generate_response.return_value = "Fresh response"

        response = router_module.route_query(
            "show payment values",
            "test-session"
        )

        execute_sql.assert_called_once_with(
            "SELECT payment_value FROM payments LIMIT 2"
        )
        self.assertEqual(response["records_found"], 2)
        self.assertEqual(len(response["data"]), 2)
        self.assertTrue(response["memory_hit"])
        self.assertEqual(response["summary"], "Fresh response")
        save_memory.assert_not_called()
        save_turn.assert_called_once()

    @patch.object(router_module, "save_query_memory")
    @patch.object(router_module, "_save_turn")
    @patch.object(router_module, "generate_response")
    @patch.object(router_module, "execute_sql_query")
    @patch.object(router_module, "generate_sql_query")
    @patch.object(router_module, "find_similar_query")
    @patch.object(router_module, "resolve_session_context")
    def test_normal_query_generates_executes_and_returns_rows(
        self,
        resolve_context,
        find_memory,
        generate_sql,
        execute_sql,
        generate_response,
        save_turn,
        save_memory
    ):
        resolve_context.return_value = (
            "test-session",
            None,
            False
        )
        find_memory.return_value = None
        generate_sql.return_value = (
            "SELECT payment_value FROM payments LIMIT 2"
        )
        execute_sql.return_value = pd.DataFrame(
            {"payment_value": [100.0, 200.0]}
        )
        generate_response.return_value = "Payment values returned"

        response = router_module.route_query(
            "show payment values",
            "test-session"
        )

        self.assertEqual(response["records_found"], 2)
        self.assertEqual(len(response["data"]), 2)
        self.assertFalse(response["memory_hit"])
        save_memory.assert_called_once()
        save_turn.assert_called_once()


class QueryExecutorTests(unittest.TestCase):
    def test_result_size_is_capped(self):
        result = execute_sql_query(
            "SELECT payment_value FROM payments",
            max_rows=10
        )

        self.assertFalse(isinstance(result, str))
        self.assertEqual(len(result), 10)


if __name__ == "__main__":
    unittest.main()
