Project Title:
Agentic AI NL to SQL Chatbot

Description:
A chatbot that converts natural language queries into SQL, executes them on a supply chain database, and returns human-readable responses.

Technologies:
- Python
- SQLite
- Groq API
- Pandas

Execution:

1. Install dependencies

pip install -r requirements.txt

2. Configure environment

Create or update the .env file with:

GROQ_API_KEY=your_groq_api_key

3. Load database

python -m modules.database_loader

4. Start chatbot API

uvicorn app.main:app --reload

Endpoints:

GET /get
POST /ask
