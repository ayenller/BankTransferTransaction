import mysql.connector
from config.config import DATABASE_CONFIG, TEST_DATABASE_CONFIG
from contextlib import contextmanager

def get_db_connection(config_type="prod"):
    try:
        # connect to test database to initiate data
        if config_type == "test":
            config = TEST_DATABASE_CONFIG
        else:
            config = DATABASE_CONFIG

        conn = mysql.connector.connect(**config)
        return conn
    except mysql.connector.Error as err:
        raise Exception(f"Database connection failed: {err}")

@contextmanager
def get_cursor(config_type="prod"):
    """Get database cursor with connection"""
    conn = get_db_connection(config_type)
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