from groq import Groq

from config.config import API_KEY

client = Groq(api_key=API_KEY)

def generate_response(
    user_query,
    sql_query,
    result,
    session_context=None
):
    result_text = result.head(10).to_string()
    context_text = "No active session context."

    if session_context:
        context_text = session_context.to_prompt_text()

    prompt = f"""

You are a helpful AI assistant.

SESSION CONTEXT:
{context_text}

USER QUESTION:
{user_query}

SQL QUERY:
{sql_query}

QUERY RESULT:
{result_text}

Explain the query result in simple
human-readable language.

"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": "You are a helpful assistant."
            },

            {
                "role": "user",
                "content": prompt
            }

        ]

    )

    return (
        response
        .choices[0]
        .message
        .content
    )
