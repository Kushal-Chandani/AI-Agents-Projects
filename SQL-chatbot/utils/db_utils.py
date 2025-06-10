import sqlite3
from typing import List, Tuple, Any

DB_PATH = 'db/data.db'

def execute_query(query: str) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    """
    Execute a SQL query and return column names and rows.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        conn.close()
        return columns, rows
    except Exception as e:
        conn.close()
        raise