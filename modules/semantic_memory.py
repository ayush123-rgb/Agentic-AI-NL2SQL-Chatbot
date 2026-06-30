import sqlite3

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config.config import DATABASE_PATH
from modules.chat_history import ensure_query_memory_table

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def find_similar_query(
    user_query,
    threshold=0.90,
    history_limit=500
):
    with sqlite3.connect(DATABASE_PATH) as conn:
        ensure_query_memory_table(conn)

        rows = conn.execute(
            f"""
            SELECT
                user_input,
                generated_sql,
                output_response
            FROM query_memory
            ORDER BY id DESC
            LIMIT {int(history_limit)}
            """
        ).fetchall()

    if not rows:
        return None

    query_embedding = model.encode(
        [user_query]
    )
    stored_embeddings = model.encode(
        [row[0] for row in rows]
    )
    similarity_scores = cosine_similarity(
        query_embedding,
        stored_embeddings
    )[0]

    best_index = int(similarity_scores.argmax())
    best_score = float(similarity_scores[best_index])
    best_match = rows[best_index]

    if best_score >= threshold:

        return {
            "input": best_match[0],
            "sql": best_match[1],
            "response": best_match[2],
            "similarity": best_score
        }

    return None
