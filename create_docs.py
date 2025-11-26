import os

print("Script started...")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Ensure docs directory exists
os.makedirs(DOCS_DIR, exist_ok=True)
print(f"Directory checked: {DOCS_DIR}")

# 1. Create Marketing Calendar
with open(os.path.join(DOCS_DIR, "marketing_calendar.md"), 'w', encoding='utf-8') as f:
    f.write("""# Northwind Marketing Calendar (1997)
## Summer Beverages 1997
- Dates: 1997-06-01 to 1997-06-30
- Notes: Focus on Beverages and Condiments.
## Winter Classics 1997
- Dates: 1997-12-01 to 1997-12-31
- Notes: Push Dairy Products and Confections for holiday gifting.""")
print("Created marketing_calendar.md")

# 2. Create KPI Definitions
with open(os.path.join(DOCS_DIR, "kpi_definitions.md"), 'w', encoding='utf-8') as f:
    f.write("""# KPI Definitions
## Average Order Value (AOV)
- AOV = SUM(UnitPrice * Quantity * (1 - Discount)) / COUNT(DISTINCT OrderID)
## Gross Margin
- GM = SUM((UnitPrice - CostOfGoods) * Quantity * (1 - Discount))
- If cost is missing, approximate with category-level average (document your approach).""")
print("Created kpi_definitions.md")

# 3. Create Catalog
with open(os.path.join(DOCS_DIR, "catalog.md"), 'w', encoding='utf-8') as f:
    f.write("""# Catalog Snapshot
- Categories include Beverages, Condiments, Confections, Dairy Products, Grains/Cereals, Meat/Poultry, Produce, Seafood.
- Products map to categories as in the Northwind DB.""")
print("Created catalog.md")

# 4. Create Product Policy
with open(os.path.join(DOCS_DIR, "product_policy.md"), 'w', encoding='utf-8') as f:
    f.write("""# Returns & Policy
- Perishables (Produce, Seafood, Dairy): 3–7 days.
- Beverages unopened: 14 days; opened: no returns.
- Non-perishables: 30 days.""")
print("Created product_policy.md")

# 5. Create Eval File
eval_content = """{"id":"rag_policy_beverages_return_days","question":"According to the product policy, what is the return window (days) for unopened Beverages? Return an integer.","format_hint":"int"}
{"id":"hybrid_top_category_qty_summer_1997","question":"During 'Summer Beverages 1997' as defined in the marketing calendar, which product category had the highest total quantity sold? Return {category:str, quantity:int}.","format_hint":"{category:str, quantity:int}"}
{"id":"hybrid_aov_winter_1997","question":"Using the AOV definition from the KPI docs, what was the Average Order Value during 'Winter Classics 1997'? Return a float rounded to 2 decimals.","format_hint":"float"}
{"id":"sql_top3_products_by_revenue_alltime","question":"Top 3 products by total revenue all-time. Revenue uses Order Details: SUM(UnitPrice*Quantity*(1-Discount)). Return list[{product:str, revenue:float}].","format_hint":"list[{product:str, revenue:float}]"}
{"id":"hybrid_revenue_beverages_summer_1997","question":"Total revenue from the 'Beverages' category during 'Summer Beverages 1997' dates. Return a float rounded to 2 decimals.","format_hint":"float"}
{"id":"hybrid_best_customer_margin_1997","question":"Per the KPI definition of gross margin, who was the top customer by gross margin in 1997? Assume CostOfGoods is approximated by 70% of UnitPrice if not available. Return {customer:str, margin:float}.","format_hint":"{customer:str, margin:float}"}"""

with open(os.path.join(BASE_DIR, 'sample_questions_hybrid_eval.jsonl'), 'w', encoding='utf-8') as f:
    f.write(eval_content)
print("Created sample_questions_hybrid_eval.jsonl")

print("All files created successfully.")