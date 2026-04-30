import sqlite3

def main_menu():
    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. Add New Product")
        print("2. View All Products")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            # Add Product Logic
            n = input("Enter Name: ")
            p = float(input("Enter Price: "))
            s = int(input("Enter Stock: "))
            
            db = sqlite3.connect('inventory.db')
            cmd = db.cursor()
            cmd.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (n, p, s))
            db.commit()
            db.close()
            print("Successfully Added!")

        elif choice == '2':
            # View Product Logic
            db = sqlite3.connect('inventory.db')
            cmd = db.cursor()
            cmd.execute("SELECT * FROM products")
            data = cmd.fetchall()
            
            print("\n--- Current Stock ---")
            for row in data:
                print(f"ID: {row[0]} | Name: {row[1]} | Price: {row[2]} | Stock: {row[3]}")
            db.close()

        elif choice == '3':
            print("Thank you for using the system!")
            break
        
        else:
            print("Invalid Choice! Please try again.")

# Run the software
main_menu()