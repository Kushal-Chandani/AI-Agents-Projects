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