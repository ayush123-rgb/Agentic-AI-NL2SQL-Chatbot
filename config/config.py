import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
DATABASE_PATH = BASE_DIR / "database" / "ecommerce_supply_chain.db"
METADATA_PATH = BASE_DIR / "database" / "metadata.json"
LOG_FILE_PATH = BASE_DIR / "logs" / "query_log.txt"

load_dotenv(ENV_PATH)

API_KEY = os.getenv("GROQ_API_KEY")
