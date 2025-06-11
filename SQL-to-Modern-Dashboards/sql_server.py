import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class SqlReadOnlyServer:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_schema(self) -> str:
        """Retrieve database schema as JSON."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        schema = {}
        try:
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [
                    {
                        "column_name": row[1],
                        "data_type": row[2],
                        "is_nullable": "YES" if row[3] == 0 else "NO",
                        "default_value": row[4],
                        "primary_key": row[5]
                    }
                    for row in cursor.fetchall()
                ]
                schema[table] = columns
        finally:
            conn.close()
        return json.dumps(schema, indent=2)

    def _execute_query(self, query: str) -> list[dict]:
        """Execute a SELECT query and return results."""
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            raise ValueError(f"Error executing query: {str(e)}")
        finally:
            conn.close()

    def handle_tool(self, tool_name: str, arguments: dict = None) -> str:
        """Handle tool calls from the agent."""
        try:
            if tool_name == "get_schema":
                return self._get_schema()
            elif tool_name == "read_query" and arguments:
                query = arguments.get("query")
                if not query:
                    raise ValueError("Query argument is required")
                return json.dumps(self._execute_query(query))
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        except Exception as e:
            return json.dumps({"error": str(e)})