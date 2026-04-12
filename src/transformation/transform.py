import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5432/ecommerce_db")

# Load data
df = pd.read_sql("SELECT * FROM raw_ecommerce_data", engine)

# Convert dates
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])

# Feature engineering
df['delivery_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
df['is_delayed'] = (df['order_delivered_customer_date'] > df['order_estimated_delivery_date']).astype(int)

# Dimension tables
dim_customers = df[['customer_id','customer_unique_id','customer_city','customer_state']].drop_duplicates()
dim_products = df[['product_id','product_category_name']].drop_duplicates()
dim_sellers = df[['seller_id','seller_city','seller_state']].drop_duplicates()

# Fact table
fact_orders = df[['order_unique_id','order_id','customer_id','product_id','seller_id',
                  'price','freight_value','payment_value','payment_type',
                  'order_purchase_timestamp','order_status',
                  'delivery_days','is_delayed']]

# Save to database
dim_customers.to_sql('dim_customers', engine, if_exists='replace', index=False)
dim_products.to_sql('dim_products', engine, if_exists='replace', index=False)
dim_sellers.to_sql('dim_sellers', engine, if_exists='replace', index=False)
fact_orders.to_sql('fact_orders', engine, if_exists='replace', index=False)

print("Transformation completed!")