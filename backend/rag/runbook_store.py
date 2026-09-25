from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import text
from backend.core.database import engine

RUNBOOKS_DIR = Path("simulator/runbooks")

async def init_vector_table():
    """Initializes the runbooks storage table with engine dialect awareness."""
    async with engine.begin() as conn:
        dialect_name = conn.dialect.name
        
        # Only execute PostgreSQL-specific extension command on Postgres
        if dialect_name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS runbooks (
                    id SERIAL PRIMARY KEY,
                    topic VARCHAR(255) NOT NULL,
                    file_source VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL
                );
            """))
        else:
            # SQLite fallback schema
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS runbooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    file_source TEXT NOT NULL,
                    content TEXT NOT NULL
                );
            """))

async def seed_runbooks():
    """Loads markdown runbooks into the database for diagnostic RAG retrieval."""
    await init_vector_table()
    
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM runbooks;"))
        
        for file in RUNBOOKS_DIR.glob("*.md"):
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
            
            await conn.execute(
                text("INSERT INTO runbooks (topic, file_source, content) VALUES (:topic, :file, :content)"),
                {"topic": file.stem.replace("_", " ").title(), "file": file.name, "content": content}
            )

async def search_runbooks(query: str, limit: int = 2) -> List[Dict[str, Any]]:
    """Retrieves relevant runbook sections using text and keyword matching."""
    keywords = [kw.lower() for kw in query.split() if len(kw) > 3]
    like_clause = "%" + "%".join(keywords[:2]) + "%" if keywords else "%timeout%"
    
    async with engine.connect() as conn:
        dialect_name = conn.dialect.name
        if dialect_name == "postgresql":
            stmt = text("SELECT topic, file_source, content FROM runbooks WHERE content ILIKE :query LIMIT :limit")
        else:
            stmt = text("SELECT topic, file_source, content FROM runbooks WHERE content LIKE :query LIMIT :limit")
            
        result = await conn.execute(stmt, {"query": like_clause, "limit": limit})
        rows = result.fetchall()
        return [
            {"topic": r[0], "file_source": r[1], "excerpt": r[2][:300] + "..."}
            for r in rows
        ]
