import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, api_key=None):
        # Use GEMINI_API_KEY or GOOGLE_API_KEY
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError('GEMINI_API_KEY environment variable not set')
        # Initialize the Gen AI client (Developer API)
        self.client = genai.Client(api_key=self.api_key)

    def generate_sql(self, prompt: str, model: str = 'gemini-2.0-flash-001') -> str:
        """
        Generate a SQL query from natural language using Gemini.
        """
        response = self.client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text.strip()