from fastapi import FastAPI

from app.router import router
from config.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Agentic AI NL to SQL Chatbot"
)

app.include_router(router)


@app.get("/get")
def get_status():
    return {
        "message": "Agentic AI NL to SQL Chatbot Running"
    }
