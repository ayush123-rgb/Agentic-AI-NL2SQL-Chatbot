import sqlite3

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config.config import DATABASE_PATH

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def find_similar_query(
    user_query,
    threshold=0.90
):
    query_embedding = model.encode(
        [user_query]
    )

    with sqlite3.connect(DATABASE_PATH) as conn:

        rows = conn.execute(
            """
            SELECT
                user_input,
                generated_sql,
                output_response
            FROM query_memory
            """
        ).fetchall()

    best_match = None
    best_score = 0

    for row in rows:

        stored_input = row[0]

        stored_embedding = model.encode(
            [stored_input]
        )

        score = cosine_similarity(
            query_embedding,
            stored_embedding
        )[0][0]

        if score > best_score:
            best_score = score
            best_match = row

    if best_score >= threshold:

        return {
            "input": best_match[0],
            "sql": best_match[1],
            "response": best_match[2],
            "similarity": best_score
        }

    return None