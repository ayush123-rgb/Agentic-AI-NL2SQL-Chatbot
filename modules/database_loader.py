import pandas as pd
import sqlite3

conn = sqlite3.connect(
    "database/ecommerce_supply_chain.db"
)

print("Database Connected Successfully")

products_df = pd.read_csv(
    "datasets/df_Products.csv"
)

orders_df = pd.read_csv(
    "datasets/df_Orders.csv"
)

payments_df = pd.read_csv(
    "datasets/df_Payments.csv"
)

orderitems_df = pd.read_csv(
    "datasets/df_OrderItems.csv"
)

customers_df = pd.read_csv(
    "datasets/df_Customers.csv"
)

print("All Datasets Loaded Successfully")

print("\nPRODUCTS DATASET")
print(products_df.head())

print("\nORDERS DATASET")
print(orders_df.head())

print("\nPAYMENTS DATASET")
print(payments_df.head())

print("\nORDER ITEMS DATASET")
print(orderitems_df.head())

print("\nCUSTOMERS DATASET")
print(customers_df.head())

products_df.to_sql(
    "products",
    conn,
    if_exists="replace",
    index=False
)

orders_df.to_sql(
    "orders",
    conn,
    if_exists="replace",
    index=False
)

payments_df.to_sql(
    "payments",
    conn,
    if_exists="replace",
    index=False
)

orderitems_df.to_sql(
    "order_items",
    conn,
    if_exists="replace",
    index=False
)

customers_df.to_sql(
    "customers",
    conn,
    if_exists="replace",
    index=False
)

print("\nAll SQL Tables Created Successfully")

cursor = conn.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table';
""")

tables = cursor.fetchall()

print("\nAVAILABLE TABLES :")

for table in tables:
    print(table[0])

conn.close()

print("\nDatabase Connection Closed")
