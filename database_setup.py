import sqlite3

db = sqlite3.connect('inventory.db')
cmd = db.cursor()

cmd.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    stock INTEGER
)
""")

db.commit()
db.close()
print("Database is ready.") 