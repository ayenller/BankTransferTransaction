import os
import sys
from datetime import datetime, timedelta
import time
import threading
import signal
import atexit
from queue import Queue, Empty

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import random
from decimal import Decimal

from database.db_connection import get_cursor, DatabaseConnectionError
from app.transfer import transfer_amount
from app.logger import setup_logger, log_error
from utils.format_utils import format_transfer_line, print_transfer_header
from utils.queue_utils import db_result_queue

stop_event = threading.Event()
transfer_stats = {'successful': 0, 'failed': 0}
stats_lock = threading.Lock()
connection_retry_delay = 5  # seconds
connection_status = {'is_connected': True}
connection_lock = threading.Lock()

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

def get_accounts(cursor):
    """Get available accounts from database"""
    cursor.execute("""
        SELECT account_id, account_name, balance 
        FROM banking_system.accounts
    """)
    accounts = cursor.fetchall()
    
    if len(accounts) < 2:
        raise ValueError("Insufficient accounts to perform transfers")
    return accounts

def get_latest_transaction(cursor):
    """Get the latest transaction record"""
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
    return cursor.fetchone()

def execute_transfers(host):
    """Thread function to execute transfers"""
    try:
        while not stop_event.is_set():
            try:
                print("#Debug A-1# time:")
                with get_cursor(host) as (cursor, conn):
                    print("#Debug A-2# time:")
                    with connection_lock:
                        connection_status['is_connected'] = True
                    print("#Debug A-3# time:")
                    try:
                        print("#Debug A-4# time:")
                        # Get 2 transfer accounts
                        try:
                            accounts = get_accounts(cursor)
                            print("#Debug A-5# time:")
                        except ValueError as e:
                            print("#Debug A-6# time:")
                            db_result_queue.put(('BUSI_ERROR', str(e)))
                            log_error(f"Insufficient accounts to perform transfers")
                            time.sleep(1)
                            continue
                        
                        print("#Debug A-7# time:")
                        # Execute transfer transaction
                        sender, receiver = random.sample(accounts, 2)
                        print("#Debug A-8# time:")
                        amount = Decimal(str(random.randrange(1, 11) * 100)).quantize(Decimal('0.00'))
                        
                        print("#Debug A-9# time:")
                        success, message = transfer_amount(
                            sender['account_id'],
                            receiver['account_id'],
                            amount,
                            cursor,
                            conn
                        )
                        
                        print("#Debug A-10# time:")
                        # Update statistics
                        with stats_lock:
                            if success:
                                print("#Debug A-11# time:")
                                transfer_stats['successful'] += 1
                                # Get & send the last transaction record
                                latest_transaction = get_latest_transaction(cursor)
                                db_result_queue.put(('SUCCESS', latest_transaction))
                            else:
                                print("#Debug A-12# time:")
                                # Business error, such as insuficient balance
                                db_result_queue.put(('BUSI_ERROR', message))
                                transfer_stats['failed'] += 1
                                time.sleep(1)
                                continue
                            
                    except Exception as e:
                        print("#Debug A-13# time:")
                        # Business exception
                        with stats_lock:
                            transfer_stats['failed'] += 1
                        print("#Debug A-14# time:")
                        db_result_queue.put(('BUSI_ERROR', f"Transaction failed: {str(e)}"))
                        print("#Debug A-15# time:")
                    time.sleep(1)  # Execute one transfer per second
                    continue
            except DatabaseConnectionError as e:
                print("#Debug A-16# time:")
                # Handle database exception
                with connection_lock:
                    connection_status['is_connected'] = False
                log_error(f"Database connection lost: {e}")
                print("#Debug A-17# time:")
                # Send database error message to queue
                db_result_queue.put(('DB_ERROR', f"Database error: {str(e)}"))
                print("#Debug A-18# time:")
                time.sleep(connection_retry_delay)
                continue
            except Exception as e:
                print("#Debug A-19# time:")
                # 处理其他异常
                log_error(f"Error in transfer: {str(e)}")
                print("#Debug A-20# time:")
                db_result_queue.put(('DB_ERROR', f"System error: {str(e)}"))
                print("#Debug A-21# time:")
                time.sleep(1)
                continue

    except Exception as e:
        print(f"Error in transfer thread: {str(e)}")
        stop_event.set()

def print_transfer_status():
    """Thread function to print transfer status"""
    current_second = 0
    last_transaction_id = None
    
    while not stop_event.is_set():
        print("#Debug 1# time:", current_second)

        # Check if current_second is a multiple of 30
        if current_second % 30 == 0:
            print("#Debug 1-1# time:", current_second)
            print_transfer_header()  # Print header every 30 seconds
        print("#Debug 1-2# time:", current_second)
        current_second += 1
        print("#Debug 1-3# time:", current_second)

        try:
            print("#Debug 1-4# time:", current_second)
            try:
                print("#Debug 1-5# time:", current_second)
                status, data = db_result_queue.get_nowait()
                print("#Debug 2# time:", current_second)

                # Successful transfer transaction
                if status == 'SUCCESS' and data and data['transaction_id'] != last_transaction_id:
                    last_transaction_id = data['transaction_id']
                    line = format_transfer_line(
                        current_second,
                        data['status'],
                        data['sender_name'],
                        data['receiver_name'],
                        data['amount'],
                        data['sender_balance_before'],
                        data['sender_balance_after'],
                        data['receiver_balance_before'],
                        data['receiver_balance_after'],
                        data['note'] or ''
                    )
                    print("#Debug 3# time:", current_second)
                    print(line)
                
                # Business error
                elif status == 'BUSI_ERROR':
                    print("#Debug 4# time:", current_second)
                    # Check if data contains full transaction info
                    if isinstance(data, dict) and data.get('amount', 0) > 0:
                        line = format_transfer_line(
                            current_second,
                            data['status'],
                            data['sender_name'],
                            data['receiver_name'],
                            data['amount'],
                            data['sender_balance_before'],
                            data['sender_balance_after'],
                            data['receiver_balance_before'],
                            data['receiver_balance_after'],
                            data['note']
                        )
                        print("#Debug 5# time:", current_second)
                    else:
                        # Basic error info
                        line = format_transfer_line(
                            current_second,
                            status,
                            note=str(data)
                        )
                        print("#Debug 6# time:", current_second)
                    print(line)
                
                # Database error
                elif status == 'DB_ERROR':
                    print("#Debug 7# time:", current_second)
                    # Check if data contains full transaction info
                    if isinstance(data, dict) and data.get('amount', 0) > 0:
                        print("#Debug 8# time:", current_second)
                        line = format_transfer_line(
                            current_second,
                            data['status'],
                            data['sender_name'],
                            data['receiver_name'],
                            data['amount'],
                            data['sender_balance_before'],
                            data['sender_balance_after'],
                            data['receiver_balance_before'],
                            data['receiver_balance_after'],
                            data['note']
                        )
                    else:
                        print("#Debug 9# time:", current_second)
                        # Basic error info
                        line = format_transfer_line(
                            current_second,
                            status,
                            note=str(data)
                        )
                        print("#Debug 10# time:", current_second)
                    print(line)
                # Database retry
                elif status == 'DB_RETRY':
                    print("#Debug 11# time:", current_second)
                    line = format_transfer_line(current_second, status, note=str(data))
                    print("#Debug 12# time:", current_second)
                    print(line)
                # Database recovery
                elif status == 'DB_RECOVERED':
                    print("#Debug 13# time:", current_second)
                    line = format_transfer_line(current_second, status, note=str(data))
                    print("#Debug 14# time:", current_second)
                    print(line)
                else:
                    print("#Debug 15# time:", current_second)
                    line = format_transfer_line(current_second, status, note=str(data))
                    print("#Debug 16# time:", current_second)
                    print(line)
            except Empty:
                print("#Debug 17# time:", current_second)
                line = format_transfer_line(current_second, 'WAIT', note='Waiting for transaction...')
                print("#Debug 18# time:", current_second)
                print(line)
                time.sleep(1)
                continue
        except Exception as e:
            print("#Debug 19# time:", current_second)
            with connection_lock:
                is_connected = connection_status['is_connected']
            print("#Debug 20# time:", current_second)
            error_data = {
                'status': 'DB_ERROR' if not is_connected else 'ERROR',
                'sender_name': 'N/A',
                'receiver_name': 'N/A',
                'amount': 0.00,
                'sender_balance_before': 0.00,
                'sender_balance_after': 0.00,
                'receiver_balance_before': 0.00,
                'receiver_balance_after': 0.00,
                'note': str(e) 
            }
            print("#Debug 21# time:", current_second)
            
            line = format_transfer_line(
                current_second,
                error_data['status'],
                error_data['sender_name'],
                error_data['receiver_name'],
                error_data['amount'],
                error_data['sender_balance_before'],
                error_data['sender_balance_after'],
                error_data['receiver_balance_before'],
                error_data['receiver_balance_after'],
                error_data['note']
            )
            print("#Debug 22# time:", current_second)
            print(line)
            time.sleep(1)
            continue
        print("#Debug 23# time:", current_second)
        time.sleep(1)

def main(duration_minutes=1, host=None):
    """Main function to start transfer system"""
    global start_time
    start_time = time.time()
    setup_logger()
    
    # Start transfer execution thread
    transfer_thread = threading.Thread(target=execute_transfers, args=(host,))
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