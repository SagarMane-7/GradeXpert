import psycopg2
import sys

# URL provided by user (without 'postgresql://' prefix for psycopg2 dsn?)
# No, psycopg2.connect accepts URI.
# Using Hostname for SNI but forcing IP via hostaddr to bypass local DNS
DATABASE_URL='postgresql://neondb_owner:npg_hfB81OmvyFuY@ep-autumn-grass-a1q7xa4i-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&hostaddr=52.220.170.93'

print(f"Testing connection to: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        print("Connection successful!")
        print(cur.fetchone())
    conn.close()
except Exception as e:
    print("Connection failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
