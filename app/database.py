import os
import aiosql
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

database_path = Path(os.getenv("DATABASE_PATH"))
queries = aiosql.from_path(Path(__file__).parents[0] / "queries.sql", "sqlite3")