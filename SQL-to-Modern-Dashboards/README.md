# SQL-to-Modern-Dashboards

A no-code, AI-powered dashboard system that connects to a SQLite database, allowing non-technical users to query data in natural language and generate interactive dashboards. Powered by the Gemini API (free tier) and Streamlit, this project eliminates data access bottlenecks by translating plain English questions into SQL queries and rendering insights as Plotly charts.

## Features

- **Natural Language Queries**: Ask questions like "Show total revenue by category" and get formatted results without writing SQL.
- **Automatic Dashboards**: Generate interactive dashboards with bar, pie, or scatter charts based on database analysis.
- **Secure Data Access**: A read-only SQL layer ensures only SELECT queries are executed, protecting your database.
- **Free and Lightweight**: Uses Gemini's free tier and SQLite, avoiding paid services.
- **Modern UI**: Streamlit interface with a dark-themed, scrollable dashboard powered by Plotly.

## Tech Stack

- **Frontend**: Streamlit 1.35.0
- **AI**: Google Gemini API (gemini-1.5-flash)
- **Database**: SQLite
- **Backend**: Python 3.9+ with sqlite3 and python-dotenv
- **Visualization**: Plotly 5.22.0

## Prerequisites

- Python 3.9 or higher: [Download Python](https://www.python.org/downloads/)
- Git: [Install Git](https://git-scm.com/)
- Gemini API Key: Sign up for a free key at [Google AI Studio](https://makersuite.google.com/).
- A code editor (e.g., VS Code) and a terminal

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Kushal-Chandani/AI-Agents-Projects.git
cd AI-Agents-Projects/SQL-to-Modern-Dashboards
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt includes:**

```
streamlit==1.35.0
google-generativeai==0.8.3
python-dotenv==1.0.1
plotly==5.22.0
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GEMINI_API_KEY=your-gemini-api-key
DB_PATH=database/sample.db
```

### 5. Initialize the SQLite Database

```bash
mkdir database
```

Create a file named `init_db.py` with the following content and run it:

```python
import sqlite3

conn = sqlite3.connect('database/sample.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        revenue REAL NOT NULL
    )
''')
sample_data = [
    ('Laptop', 'Electronics', 10, 12000.0),
    ('Phone', 'Electronics', 15, 9000.0),
    ('Shirt', 'Clothing', 50, 1500.0),
    ('Jeans', 'Clothing', 30, 1800.0),
    ('Headphones', 'Electronics', 20, 2000.0),
]
cursor.executemany('INSERT INTO sales (product, category, quantity, revenue) VALUES (?, ?, ?, ?)', sample_data)
conn.commit()
conn.close()
print("Database initialized successfully.")
```

Run the script:

```bash
python init_db.py
```

You can delete `init_db.py` after running it.

### 6. Run the Application

```bash
streamlit run app.py
```

Open your browser to [http://localhost:8501](http://localhost:8501)

## Usage

### Chatbot Tab

- **Purpose**: Query the database in natural language.
- **How to Use**: Enter questions like “Show total revenue by category” or “List products with quantity > 20”.
- **Example Output**:

```
The query calculates the total revenue for each category in the sales table.

Results:
category: Electronics, total_revenue: 23000.0
category: Clothing, total_revenue: 3300.0
```

### Dashboard Tab

- **Purpose**: Generate interactive dashboards with Plotly charts.
- **How to Use**: Click “Generate Dashboard” to let the AI render visualizations.
- **Features**: Download dashboard as HTML.

**Example Output**:

- **Bar chart**: Revenue by category (Electronics: $23,000, Clothing: $3,300)
- **Pie chart**: Quantity distribution by product