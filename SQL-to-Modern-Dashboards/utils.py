import json
from typing import Dict, Any

def validate_dashboard_json(json_str: str) -> Dict[str, Any]:
    """Validate the structure of dashboard JSON."""
    try:
        data = json.loads(json_str)
        required_keys = ["domain", "key_metrics", "dashboard_components"]
        if not all(key in data for key in required_keys):
            raise ValueError("Missing required keys in JSON")
        for metric in data["key_metrics"]:
            if not all(k in metric for k in ["name", "sql_query", "chart_type"]):
                raise ValueError("Invalid metric structure")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")