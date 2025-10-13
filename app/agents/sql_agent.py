import psycopg2
from groq import Groq
from fastapi import HTTPException
from langchain_core.tools import tool
from app.core.config import GROQ_API_KEY
from typing import Dict, Any
from app.config.config import Settings
from langchain_community.tools import DuckDuckGoSearchRun
from ..db.database import get_session
from sqlmodel import text

client = Groq(api_key=GROQ_API_KEY)


@tool
def fetch_database_schema()->Dict[str,Any]:
    """
    Fetch the database schema (tables, columns, and types) from a PostgreSQL database.
    """
    # conn = psycopg2.connect(Settings().DATABASE_URL)
    # cur = conn.cursor()
    try:
        query = text("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """)

        # cur.execute(query)
        # rows = cur.fetchall()
        # cur.close()
        # conn.close()

        schema = {}

        for session in get_session():
            result = session.exec(query).all()
    
        for table, col, dtype in result:
            schema.setdefault(table, []).append({"column": col, "type": dtype})

        print("Fetched Schema:", schema)

        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@tool
def generate_and_execute_select_query(prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a SQL SELECT query from a natural language prompt and schema.
    """
    try:
        schema_str = "\n".join(
            [f"{tbl}: {', '.join([c['column'] for c in cols])}" for tbl, cols in schema.items()]
        )

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                    "You are a PostgreSQL SQL generator. "
            "Return ONLY the raw SQL query — no explanations, "
            "no markdown, no ``` fences. "
            "Always use PostgreSQL syntax and double quotes for identifiers.\n"
            f"Schema:\n{schema_str}"
                ),
                },
                {"role": "user", "content": prompt},
            ],
        )   

        query = response.choices[0].message.content.strip()
        print("Generated SQL:", query)

        dangerous_keywords = ["delete", "update", "insert", "drop", "alter", "create", "truncate"]
        if any(word in query.lower() for word in dangerous_keywords):
            raise HTTPException(status_code=400, detail="Unsafe SQL detected. Only SELECT queries are allowed.")
        

        print("Final Safe SQL:", query)

        if not query.strip().lower().startswith("select"):
            raise HTTPException(status_code=400, detail="Only SELECT queries are permitted.")

        # conn = psycopg2.connect(Settings().DATABASE_URL)
        # cur = conn.cursor()
        # cur.execute(query)
        # rows = cur.fetchall()
        # col_names = [desc[0] for desc in cur.description]
        # cur.close()
        # conn.close()
        q = text(query)

        for session in get_session():
            result = session.exec(q)
            rows = result.all()
            col_names = [desc[0] for desc in result.cursor.description]

        return {"query": query, "columns": col_names, "rows": rows} 

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@tool
def search_web(query: str) -> str:
    """
    Search the web for CURRENT/RECENT information that changes frequently.
    Use this tool ONLY for:
    - Current events, breaking news, today's updates
    - Real-time data (stock prices, weather, sports scores)
    - Recent information after 2024
    - Facts that change frequently (someone's current age, latest records)
    
    DO NOT use for:
    - General knowledge the LLM already knows
    - Historical facts
    - Static information
    
    Args:
        query: The search query
        
    Returns:
        Search results as a string
    """
    try:
        search = DuckDuckGoSearchRun()
        result = search.run(query)
        return result
    except Exception as e:
        return f"Search failed: {str(e)}"