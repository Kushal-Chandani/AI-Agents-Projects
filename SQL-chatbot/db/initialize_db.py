import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')
CSV_PATH = os.path.join(os.getcwd(), 'Connections.csv')

def init_db():
    """
    Initialize the SQLite database from the CSV.
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH)
    df.to_sql('connections', conn, if_exists='replace', index=False)
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized at data.db")