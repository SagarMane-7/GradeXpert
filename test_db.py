import os
from sqlalchemy import create_engine, text

# URL provided by user
DATABASE_URL='postgresql://neondb_owner:npg_hfB81OmvyFuY@ep-autumn-grass-a1q7xa4i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'

print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Connection successful!")
        print(result.fetchone())
except Exception as e:
    print("Connection failed!")
    print(e)
