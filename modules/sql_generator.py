from groq import Groq

from config.config import API_KEY

from modules.schema_extractor import schema

client = Groq(api_key=API_KEY)


def generate_sql_query(user_query):

    
    prompt = f"""

You are an expert SQL query generator.

Convert Natural Language query into SQLite SQL query.

IMPORTANT RULES:

1. Generate ONLY SELECT queries
2. Never generate DELETE queries
3. Never generate DROP queries
4. Never generate UPDATE queries
5. Never generate ALTER queries
6. Never generate INSERT queries
7. Use SQLite syntax only
8. Return ONLY SQL query
9. Use proper JOIN conditions
10. Avoid nested subqueries
11. Prefer optimized SQL queries
12. Use direct table relationships
13. Use LIMIT whenever suitable
14. Avoid unnecessary columns
15. Generate efficient queries

DATABASE SCHEMA:

{schema}

TABLE RELATIONSHIPS:

orders.customer_id = customers.customer_id

payments.order_id = orders.order_id

order_items.order_id = orders.order_id

order_items.product_id = products.product_id

USER QUESTION:

{user_query}

"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": "You are a SQL expert."
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

    sql_query = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    sql_query = sql_query.replace(
        "```sql",
        ""
    )

    sql_query = sql_query.replace(
        "```",
        ""
    )

    return sql_query
