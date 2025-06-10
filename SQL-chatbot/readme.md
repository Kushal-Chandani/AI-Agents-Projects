# SQL Chatbot Project

A Streamlit-based conversational AI assistant that converts natural language into SQL queries using the Google Gemini API, runs them on a local SQLite database, and displays results interactively.

## Setup

1. Clone this repo and place your csv in the root directory.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows use venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set your Gemini API key as an environment variable:
   ```bash
   export GEMINI_API_KEY="YOUR_KEY"  # Windows: set GEMINI_API_KEY=YOUR_KEY
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Features

- Natural language → SQL conversion
- Interactive chat interface
- Live query execution on SQLite
- SQL syntax guidance
