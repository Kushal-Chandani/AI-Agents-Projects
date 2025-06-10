from utils.gemini_client import GeminiClient

class SQLGenerator:
    def __init__(self, api_key=None):
        self.client = GeminiClient(api_key)

    def nl_to_sql(self, nl_query: str) -> str:
        # Construct a robust prompt to handle name splitting and case-insensitive matching
        prompt = (
            "You are an expert SQL assistant for a SQLite table named 'connections' with columns: "
            "first_name, last_name, user_id, URL, Company, Position, goals, preferences, communication_style. "
            "When matching names, perform case-insensitive comparison. "
            "If the user provides a full name (e.g., 'John Doe'), split on whitespace: use the first token as first_name and the last token as last_name. "
            "If only one name is given, match it against either first_name or last_name. "
            "Convert the following user request into a valid SQL SELECT query. "
            f"Request: {nl_query}\n"
            "Respond with only the SQL query, and do not include code fences."
        )
        return self.client.generate_sql(prompt)