import os
import json
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from sql_server import SqlReadOnlyServer

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

async def run_chat_agent(message: str) -> str:
    """Handle natural language database queries."""
    db = SqlReadOnlyServer(os.getenv("DB_PATH"))
    schema = db.handle_tool("get_schema")
    
    prompt = f"""
    Given the database schema:
    {schema}
    
    User question: {message}
    
    Generate a SELECT query to retrieve the requested data and explain the results in plain English. Only generate SQL queries that start with SELECT. Non-SELECT queries (e.g., INSERT, UPDATE, DELETE) are not allowed.
    Return JSON:
    {{
        "query": "SELECT ...",
        "explanation": "string"
    }}
    """
    
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        json_str = response.text.strip("```json\n").strip("```")
        print(f"Generated JSON (run_chat_agent): {json_str}")  # Debugging
        result = json.loads(json_str)
        
        if "query" not in result or "explanation" not in result:
            return "Error: Invalid response format from AI model."
        
        query = result["query"]
        print(f"Executing query: {query}")  # Debugging
        query_result = db.handle_tool("read_query", {"query": query})
        
        try:
            data = json.loads(query_result)
            if isinstance(data, dict) and "error" in data:
                return f"Error executing query: {data['error']} (Query: {query})"
            if not isinstance(data, list):
                return f"Error: Query result is not a list of records (Query: {query})."
        except json.JSONDecodeError:
            return f"Error: Failed to parse query results (Query: {query})."
        
        explanation = f"{result['explanation']}\n\nResults:\n"
        if data:
            for row in data[:5]:
                explanation += ", ".join(f"{k}: {v}" for k, v in row.items()) + "\n"
        else:
            explanation += "No data found."
        
        return explanation
    
    except json.JSONDecodeError:
        return "Error: Failed to parse AI response as JSON."
    except Exception as e:
        return f"Error: {str(e)}"