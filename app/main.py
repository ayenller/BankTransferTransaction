import os
import sys
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import random
from decimal import Decimal

from database.db_connection import get_cursor
from app.transfer import transfer_amount
from app.logger import setup_logger

def execute_random_transfers(num_transfers=10):
    """Execute random transfer transactions"""
    setup_logger()
    
    # Only print header on first call
    if not hasattr(execute_random_transfers, 'header_printed'):
        print("\nStarting transfer transactions...")
        print("-" * 130)
        print("Time                 Status   Sender             Receiver             Amount         Sender Balance        Receiver Balance")
        print("-" * 130)
        execute_random_transfers.header_printed = True
    
    try:
        with get_cursor() as (cursor, conn):
            # Get all account information
            cursor.execute("""
                SELECT account_id, account_name, balance 
                FROM banking_system.accounts
            """)
            accounts = cursor.fetchall()
            
            if len(accounts) < 2:
                print("Insufficient accounts to perform transfers")
                return
            
            successful_transfers = 0
            failed_transfers = 0
            
            for i in range(num_transfers):
                # Randomly select sender and receiver
                sender, receiver = random.sample(accounts, 2)
                # Generate random transfer amount (between 100-1000, multiples of 100)
                amount = Decimal(str(random.randrange(1, 11) * 100)).quantize(Decimal('0.00'))
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Execute transfer
                success, message = transfer_amount(
                    sender['account_id'],
                    receiver['account_id'],
                    amount,
                    cursor,
                    conn
                )
                
                # Get balances after transfer
                if success:
                    cursor.execute("""
                        SELECT account_name, balance 
                        FROM banking_system.accounts 
                        WHERE account_id IN (%s, %s)
                    """, (sender['account_id'], receiver['account_id']))
                    updated_balances = cursor.fetchall()
                    
                    status = "SUCCESS"
                    sender_balance_after = updated_balances[0]['balance']
                    receiver_balance_after = updated_balances[1]['balance']
                else:
                    status = "FAILED"
                    sender_balance_after = sender['balance']
                    receiver_balance_after = receiver['balance']
                
                # Single line format output
                print(f"{current_time}  {status:<8} {sender['account_name']:<18} {receiver['account_name']:<18} "
                      f"{amount:>8.2f} CNY    "
                      f"{sender['balance']:>8.2f}->{sender_balance_after:<8.2f}    "
                      f"{receiver['balance']:>8.2f}->{receiver_balance_after:<8.2f}")
                
                if success:
                    successful_transfers += 1
                else:
                    failed_transfers += 1
            
    except Exception as e:
        print(f"Error during transfer execution: {str(e)}")

if __name__ == "__main__":
    execute_random_transfers(10) 