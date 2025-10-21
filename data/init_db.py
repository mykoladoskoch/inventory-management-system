"""
Database Initialization Script
Creates the SQLite database and tables for the inventory management system.
"""
import sqlite3
import os

def init_database():
    """
    Initialize the database with required tables.
    Creates products and orders tables if they don't exist.
    """
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'inventory.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock_level INTEGER NOT NULL
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_date TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        line_items TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at: {db_path}")
    print("Tables created: products, orders")

if __name__ == "__main__":
    init_database()
