import sqlite3

# Simple function to add product
def add_data():
    # Input from user
    n = input("Enter Name: ")
    p = float(input("Enter Price: "))
    s = int(input("Enter Stock: "))

    # Connect to database
    db = sqlite3.connect('inventory.db')
    cmd = db.cursor()

    # Simple SQL query
    q = "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)"
    val = (n, p, s)
    
    cmd.execute(q, val)
    
    db.commit()
    db.close()
    print("Done! Data Saved.")

# Call the function
add_data()