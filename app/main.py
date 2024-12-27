import os
import sys
from datetime import datetime, timedelta
import time
import threading
import signal
import atexit
import queue

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import random
from decimal import Decimal

from database.db_connection import get_cursor
from app.transfer import transfer_amount
from app.logger import setup_logger

stop_event = threading.Event()
transfer_stats = {'successful': 0, 'failed': 0}
stats_lock = threading.Lock()

def signal_handler(signum, frame):
    stop_event.set()
    print("\n\nProgram terminating, please wait...")
    time.sleep(2)
    print_summary(time.time() - start_time)
    sys.exit(0)

def cleanup():
    stop_event.set()
    time.sleep(1)

def print_summary(total_time):
    """Print transfer summary"""
    print("\nTransfer Summary:")
    print(f"Successful transfers: {transfer_stats['successful']}")
    print(f"Failed transfers: {transfer_stats['failed']}")
    print(f"Total time: {total_time:.2f} seconds")

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
atexit.register(cleanup)

def execute_transfers():
    """Thread function to execute transfers"""
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
            
            while not stop_event.is_set():
                # Randomly select sender and receiver
                sender, receiver = random.sample(accounts, 2)
                amount = Decimal(str(random.randrange(1, 11) * 100)).quantize(Decimal('0.00'))
                
                try:
                    success, message = transfer_amount(
                        sender['account_id'],
                        receiver['account_id'],
                        amount,
                        cursor,
                        conn
                    )
                    
                    with stats_lock:
                        if success:
                            transfer_stats['successful'] += 1
                        else:
                            transfer_stats['failed'] += 1
                            
                except Exception as e:
                    with stats_lock:
                        transfer_stats['failed'] += 1
                
                time.sleep(1)  # Execute one transfer per second
                
    except Exception as e:
        print(f"Error in transfer thread: {str(e)}")
        stop_event.set()

def print_transfer_status():
    """Thread function to print transfer status"""
    current_second = 0
    last_transaction_id = None
    
    # Print header
    print("\nStarting transfer transactions...")
    print("-" * 150)
    print("Time   Status   Sender             Receiver             Amount         Sender Balance        Receiver Balance     Note")
    print("-" * 150)
    
    while not stop_event.is_set():
        current_second += 1
        
        try:
            with get_cursor() as (cursor, conn):
                # Get the latest transaction
                cursor.execute("""
                    SELECT 
                        t.transaction_id,
                        t.status,
                        t.amount,
                        t.created_at,
                        s.account_name as sender_name,
                        r.account_name as receiver_name,
                        t.sender_balance_before,
                        t.sender_balance_after,
                        t.receiver_balance_before,
                        t.receiver_balance_after,
                        t.note
                    FROM banking_system.transactions t
                    JOIN banking_system.accounts s ON t.sender_id = s.account_id
                    JOIN banking_system.accounts r ON t.receiver_id = r.account_id
                    ORDER BY t.created_at DESC
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row and row['transaction_id'] != last_transaction_id:
                    last_transaction_id = row['transaction_id']
                    status = row['status']
                    print(f"{current_second:>3}s   {status:<8} {row['sender_name']:<18} {row['receiver_name']:<18} "
                          f"{row['amount']:>8.2f} USD    "
                          f"{row['sender_balance_before']:>8.2f}->{row['sender_balance_after']:<8.2f}    "
                          f"{row['receiver_balance_before']:>8.2f}->{row['receiver_balance_after']:<8.2f}    "
                          f"{row['note'] or ''}")
                else:
                    print(f"{current_second:>3}s   {'WAIT':<8} {'N/A':<18} {'N/A':<18} "
                          f"{'0.00':>8} USD    "
                          f"{'0.00':>8}->{0.00:<8}    "
                          f"{'0.00':>8}->{0.00:<8}    "
                          f"Waiting for transaction...")
        except Exception as e:
            print(f"{current_second:>3}s   {'ERROR':<8} {'N/A':<18} {'N/A':<18} "
                  f"{'0.00':>8} USD    "
                  f"{'0.00':>8}->{0.00:<8}    "
                  f"{'0.00':>8}->{0.00:<8}    "
                  f"{str(e)[:50]}...")
        
        time.sleep(1)

def main(duration_minutes=1):
    """Main function to start transfer system"""
    global start_time
    start_time = time.time()
    setup_logger()
    
    # Start transfer execution thread
    transfer_thread = threading.Thread(target=execute_transfers)
    transfer_thread.daemon = True
    transfer_thread.start()
    
    # Start status printing thread
    printer_thread = threading.Thread(target=print_transfer_status)
    printer_thread.daemon = True
    printer_thread.start()
    
    # Wait for specified duration
    try:
        time.sleep(duration_minutes * 60)
        stop_event.set()
        time.sleep(2)  # Wait for threads to finish
        print_summary(time.time() - start_time)
    except KeyboardInterrupt:
        stop_event.set()
        time.sleep(2)
        print_summary(time.time() - start_time)

if __name__ == "__main__":
    main(1)  # Run for 1 minute by default 