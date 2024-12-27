import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from database.db_connection import get_cursor

def create_tables(cursor):
    """Create database tables"""
    cursor.execute("""
    CREATE DATABASE IF NOT EXISTS banking_system;
    """)
    
    cursor.execute("""
    USE banking_system;
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id BIGINT AUTO_RANDOM,
        account_name VARCHAR(100) NOT NULL DEFAULT '',
        balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        PRIMARY KEY (account_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id BIGINT AUTO_RANDOM,
        sender_id BIGINT NOT NULL,
        receiver_id BIGINT NOT NULL,
        amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        status VARCHAR(20) NOT NULL,
        sender_balance_before DECIMAL(10, 2) NOT NULL,
        sender_balance_after DECIMAL(10, 2) NOT NULL,
        receiver_balance_before DECIMAL(10, 2) NOT NULL,
        receiver_balance_after DECIMAL(10, 2) NOT NULL,
        note VARCHAR(200),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (transaction_id),
        FOREIGN KEY (sender_id) REFERENCES banking_system.accounts(account_id),
        FOREIGN KEY (receiver_id) REFERENCES banking_system.accounts(account_id)
    );
    """)

if __name__ == "__main__":
    with get_cursor() as (cursor, conn):
        create_tables(cursor)
        print("create tables success!") 