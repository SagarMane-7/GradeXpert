import os
import psycopg2
from psycopg2.extras import RealDictCursor

NEON_DB_URL = os.environ.get('DATABASE_URL', '')

class PGResultWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        try:
            self.rows = cursor.fetchall()
        except Exception:
            self.rows = []
        self.lastrowid = getattr(cursor, 'lastrowid', None)

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows

class PGWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, query, params=()):
        # Replace SQLite ? placeholder with PostgreSQL %s
        pg_query = query.replace('?', '%s')
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(pg_query, params)
        return PGResultWrapper(cursor)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def get_pg_db():
    """Get PostgreSQL connection wrapped with SQLite-compatible API."""
    if not NEON_DB_URL:
        return None
    conn = psycopg2.connect(NEON_DB_URL)
    conn.autocommit = False
    return PGWrapper(conn)

