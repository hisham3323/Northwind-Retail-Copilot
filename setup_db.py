import os
import urllib.request
import sqlite3

# Define paths
data_dir = "data"
db_path = os.path.join(data_dir, "northwind.sqlite")
url = "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/main/dist/northwind.db"

# Ensure data directory exists
os.makedirs(data_dir, exist_ok=True)

# 1. Download the Database
print(f"Downloading Northwind DB from {url}...")
try:
    urllib.request.urlretrieve(url, db_path)
    print(f"Database saved to {db_path}")
except Exception as e:
    print(f"Error downloading: {e}")
    exit(1)

# 2. Create Compatibility Views
print("Creating compatibility views...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL to create lowercase views
    sql_script = """
    CREATE VIEW IF NOT EXISTS orders AS SELECT * FROM Orders;
    CREATE VIEW IF NOT EXISTS order_items AS SELECT * FROM "Order Details";
    CREATE VIEW IF NOT EXISTS products AS SELECT * FROM Products;
    CREATE VIEW IF NOT EXISTS customers AS SELECT * FROM Customers;
    """
    
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Views created successfully.")
    
except Exception as e:
    print(f"Error executing SQL: {e}")