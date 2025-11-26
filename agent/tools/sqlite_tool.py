import sqlite3
import pandas as pd
from typing import List, Dict, Union, Any
import os

class SQLiteDB:
    def __init__(self, db_path: str):
        """
        Initialize with path to the SQLite database.
        """
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found at {db_path}")

    def execute_query(self, sql: str) -> Union[List[Dict[str, Any]], str]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        Returns an error string if execution fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Use pandas for easy conversion to dict, but handles simple selects well
                df = pd.read_sql_query(sql, conn)
                return df.to_dict(orient="records")
        except Exception as e:
            return f"Error executing SQL: {str(e)}"

    def get_schema(self, table_names: List[str] = None) -> str:
        """
        Returns the schema definition for specified tables using PRAGMA.
        If table_names is None, returns schema for all tables.
        """
        schema_str = ""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # If no specific tables requested, get all tables
                if not table_names:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    table_names = [row[0] for row in cursor.fetchall()]

                for table in table_names:
                    schema_str += f"Table: {table}\n"
                    cursor.execute(f"PRAGMA table_info('{table}')")
                    columns = cursor.fetchall()
                    # format: (cid, name, type, notnull, dflt_value, pk)
                    for col in columns:
                        schema_str += f"  - {col[1]} ({col[2]})\n"
                    schema_str += "\n"
                    
            return schema_str
        except Exception as e:
            return f"Error retrieving schema: {str(e)}"

# Quick test block to verify it works when run directly
if __name__ == "__main__":
    # Adjust path if running from agent/tools/ directly vs project root
    # Assuming running from project root context or adjusting relative path
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/northwind.sqlite"))
    
    print(f"Testing DB connection to: {base_path}")
    if os.path.exists(base_path):
        db = SQLiteDB(base_path)
        print("--- Schema ---")
        print(db.get_schema(["products", "orders"]))
        print("--- Sample Query ---")
        print(db.execute_query("SELECT ProductName, UnitPrice FROM products LIMIT 3"))
    else:
        print("Database file not found for testing. Check path.")