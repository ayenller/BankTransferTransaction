import mysql.connector
from config.config import DATABASE_CONFIG
from contextlib import contextmanager

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as err:
        raise Exception(f"Database connection failed: {err}")

@contextmanager
def get_cursor():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor, conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close() 