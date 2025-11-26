import dspy

# -------------------------------------------------------------------------
# Bare Metal Signatures (Text Only)
# -------------------------------------------------------------------------

class RouterSignature(dspy.Signature):
    """
    Classify the question.
    - If it asks for 'how many', 'quantity', 'revenue', 'top', 'average': output 'sql'.
    - If it asks for 'dates', 'policy', 'notes': output 'rag'.
    - If it needs both (e.g. 'revenue during Summer 1997'): output 'hybrid'.
    
    Answer with exactly one word: rag, sql, or hybrid.
    """
    question = dspy.InputField()
    answer = dspy.OutputField(desc="The tool name")

class GenerateSQLSignature(dspy.Signature):
    """
    Write a SQLite query.
    
    SCHEMA:
    - orders (OrderID, OrderDate, CustomerID)
    - order_items (OrderID, ProductID, UnitPrice, Quantity, Discount)
    - products (ProductID, ProductName, CategoryID, SupplierID)
    - categories (CategoryID, CategoryName)
    - customers (CustomerID, CompanyName)
    
    --- CHEAT SHEET EXAMPLES ---
    
    Q: Top 3 products by revenue?
    SQL: SELECT p.ProductName, SUM(oi.UnitPrice * oi.Quantity * (1 - oi.Discount)) AS Rev FROM order_items oi JOIN products p ON oi.ProductID = p.ProductID GROUP BY p.ProductName ORDER BY Rev DESC LIMIT 3;
    
    Q: Revenue for Beverages in June 1997?
    SQL: SELECT SUM(oi.UnitPrice * oi.Quantity * (1 - oi.Discount)) FROM orders o JOIN order_items oi ON o.OrderID = oi.OrderID JOIN products p ON oi.ProductID = p.ProductID JOIN categories c ON p.CategoryID = c.CategoryID WHERE c.CategoryName = 'Beverages' AND o.OrderDate LIKE '1997-06%';
    
    Q: Average Order Value (AOV) in Dec 1997?
    SQL: SELECT SUM(oi.UnitPrice * oi.Quantity * (1 - oi.Discount)) / COUNT(DISTINCT o.OrderID) FROM orders o JOIN order_items oi ON o.OrderID = oi.OrderID WHERE o.OrderDate LIKE '1997-12%';
    
    Q: Top Category by quantity in June 1997?
    SQL: SELECT c.CategoryName, SUM(oi.Quantity) as Qty FROM orders o JOIN order_items oi ON o.OrderID = oi.OrderID JOIN products p ON oi.ProductID = p.ProductID JOIN categories c ON p.CategoryID = c.CategoryID WHERE o.OrderDate LIKE '1997-06%' GROUP BY c.CategoryName ORDER BY Qty DESC LIMIT 1;
    
    --- END EXAMPLES ---
    
    Output the SQL string only.
    """
    question = dspy.InputField()
    schema_context = dspy.InputField()
    sql_query = dspy.OutputField()

class SynthesizerSignature(dspy.Signature):
    """
    Answer the question based on the provided context.
    - If the context has a number, output it.
    - If the context is empty, say "Could not determine".
    """
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField()