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

async def analyze_database(message: str, db: SqlReadOnlyServer) -> dict:
    """Analyze database schema and suggest metrics."""
    schema = db.handle_tool("get_schema")
    prompt = f"""
    Given the database schema:
    {schema}
    
    User request: {message}
    
    Suggest key metrics and dashboard components in JSON format. Only generate SQL queries that start with SELECT for data retrieval. Non-SELECT queries (e.g., INSERT, UPDATE, DELETE) are not allowed.
    Return JSON:
    {{
        "domain": "string",
        "key_metrics": [{{"name": "string", "sql_query": "SELECT ...", "chart_type": "string"}}],
        "dashboard_components": ["string"]
    }}
    """
    try:
        response = await asyncio.to_thread(model.generate_content, prompt)
        json_str = response.text.strip("```json\n").strip("```")
        print(f"Generated JSON (analyze_database): {json_str}")  # Debugging
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse AI response as JSON.")
    except Exception as e:
        raise ValueError(f"Error in schema analysis: {str(e)}")

async def get_data_from_database(analysis: dict, db: SqlReadOnlyServer) -> dict:
    """Fetch data based on analysis."""
    data = {"metrics": []}
    for metric in analysis["key_metrics"]:
        query = metric["sql_query"]
        print(f"Executing query: {query}")  # Debugging
        try:
            results = json.loads(db.handle_tool("read_query", {"query": query}))
            if isinstance(results, dict) and "error" in results:
                raise ValueError(f"Query error: {results['error']} (Query: {query})")
            data["metrics"].append({
                "name": metric["name"],
                "chart_type": metric["chart_type"],
                "data": results
            })
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse query results for: {query}")
        except ValueError as e:
            raise ValueError(f"{str(e)} (Query: {query})")
    return data

async def generate_html_dashboard(data: dict) -> str:
    """Generate HTML dashboard with chart data for Plotly."""
    charts = []
    for idx, metric in enumerate(data["metrics"]):
        chart_type = metric["chart_type"].lower()
        results = metric["data"]
        if not results:
            continue

        if chart_type == "bar":
            x = [row[list(row.keys())[0]] for row in results]
            y = [row[list(row.keys())[1]] for row in results]
            charts.append({
                "id": f"chart{idx + 1}",
                "title": metric["name"],
                "type": "bar",
                "x": x,
                "y": y
            })
        elif chart_type == "pie":
            labels = [row[list(row.keys())[0]] for row in results]
            values = [row[list(row.keys())[1]] for row in results]
            charts.append({
                "id": f"chart{idx + 1}",
                "title": metric["name"],
                "type": "pie",
                "labels": labels,
                "values": values
            })
        elif chart_type == "scatter":
            x = [row[list(row.keys())[0]] for row in results]
            y = [row[list(row.keys())[1]] for row in results]
            charts.append({
                "id": f"chart{idx + 1}",
                "title": metric["name"],
                "type": "scatter",
                "x": x,
                "y": y
            })

    with open("templates/dashboard.html", "r") as file:
        template = file.read()

    charts_json = json.dumps(charts, indent=2)
    html_content = template.replace('const charts = [];', f'const charts = {charts_json};')
    return html_content

async def run_dashboard_agent(message: str) -> str:
    """Main dashboard generation pipeline."""
    db = SqlReadOnlyServer(os.getenv("DB_PATH"))
    
    try:
        analysis = await analyze_database(message, db)
        data = await get_data_from_database(analysis, db)
        html = await generate_html_dashboard(data)
        return html
    except Exception as e:
        raise ValueError(f"Dashboard generation failed: {str(e)}")