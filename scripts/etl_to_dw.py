import pandas as pd
import sqlite3
import pathlib
import sys

# For local imports, temporarily add project root to sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Constants
DW_DIR = pathlib.Path("data").joinpath("dw")
DB_PATH = DW_DIR.joinpath("smart_sales.db")
PREPARED_DATA_DIR = pathlib.Path("data").joinpath("prepared")

def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create tables in the data warehouse if they don't exist."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            join_date TEXT,
            loyalty_points INTEGER,
            preferred_contact_method TEXT      
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            unit_price NUMERIC,
            stock_quantity INTEGER,
            supplier TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale (
            sale_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            sale_amount REAL,
            sale_date TEXT,
            "store_id" INTEGER,
            "campaign_id" INTEGER,
            "discount_percent" NUMERIC,
            "state" TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
            FOREIGN KEY (product_id) REFERENCES product (product_id)
        )
    """)

def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from the customer, product, and sale tables."""
    cursor.execute("DELETE FROM customer")
    cursor.execute("DELETE FROM product")
    cursor.execute("DELETE FROM sale")

def insert_customers(customers_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Rename customer data columns to match the database schema and insert into the table."""
    customers_df.rename(columns={
        "CustomerID": "customer_id",
        "Name": "name",
        "Region": "region",
        "JoinDate": "join_date",
        "LoyaltyPoints": "loyalty_points",
        "CustomerSegment": "customer_segment",
        "StandardDateTime": "standard_datetime",
        "PreferredContactMethod": "preferred_contact_method"
    }, inplace=True)

    customers_df.to_sql("customer", cursor.connection, if_exists="append", index=False) 

def insert_products(products_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    products_df.rename(columns={
        "ProductID": "product_id",
        "ProductName": "product_name",
        "Category": "category",
        "UnitPrice": "unit_price",
        "StockQuantity": "stock_quantity",
        "Supplier": "supplier"
    }, inplace=True)

    products_df.to_sql("product", cursor.connection, if_exists="append", index=False)

def insert_sales(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    sales_df.rename(columns={
        "TransactionID": "sale_id",
        "CustomerID": "customer_id",
        "ProductID": "product_id",
        "SaleAmount": "sale_amount",
        "SaleDate": "sale_date",
        "StoreID": "store_id",
        "CampaignID": "campaign_id",
        "DiscountPercent": "discount_percent",
        "State": "state"
    }, inplace=True)

    sales_df.to_sql("sale", cursor.connection, if_exists="append", index=False)

def load_data_to_db() -> None:
    try:
        # Connect to SQLite – will create the file if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create schema and clear existing records
        create_schema(cursor)
        delete_existing_records(cursor)

        # Load prepared data using pandas
        customers_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("customers_data_prepared.csv"))
        products_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("products_data_prepared.csv"))
        sales_df = pd.read_csv(PREPARED_DATA_DIR.joinpath("sales_data_prepared.csv"))

        # Insert data into the database
        insert_customers(customers_df, cursor)
        insert_products(products_df, cursor)
        insert_sales(sales_df, cursor)

        conn.commit()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data_to_db()