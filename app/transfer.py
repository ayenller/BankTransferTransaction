from decimal import Decimal
from app.logger import log_transaction, log_error

def transfer_amount(sender_id, receiver_id, amount, cursor, conn, elapsed_seconds=0):
    try:
        print("#Debug B-1# time:")
        # Check the balance of sender
        cursor.execute(
            "SELECT account_id, balance FROM accounts WHERE account_id IN (%s, %s) FOR UPDATE",
            (sender_id, receiver_id)
        )
        accounts = {row['account_id']: row['balance'] for row in cursor.fetchall()}
        
        sender_balance_before = accounts.get(sender_id, 0)
        receiver_balance_before = accounts.get(receiver_id, 0)
        
        print("#Debug B-2# time:")
        if not sender_balance_before or sender_balance_before < amount:
            # Get account names for error message
            cursor.execute(
                "SELECT account_id, account_name FROM accounts WHERE account_id IN (%s, %s)",
                (sender_id, receiver_id)
            )
            print("#Debug B-3# time:")
            account_names = {row['account_id']: row['account_name'] for row in cursor.fetchall()}
            
            error_data = {
                'status': 'FAILED',
                'sender_name': account_names.get(sender_id, 'N/A'),
                'receiver_name': account_names.get(receiver_id, 'N/A'),
                'amount': amount,
                'sender_balance_before': sender_balance_before,
                'sender_balance_after': sender_balance_before,
                'receiver_balance_before': receiver_balance_before,
                'receiver_balance_after': receiver_balance_before,
                'note': 'Insufficient balance'
            }
            print("#Debug B-4# time:")
            log_transaction(
                sender_id, receiver_id, amount, "FAILED",
                sender_balance_before, receiver_balance_before,
                sender_balance_before, receiver_balance_before,
                "Insufficient balance",
                elapsed_seconds
            )
            print("#Debug B-5# time:")
            # Insert failed transaction record
            cursor.execute("""
                INSERT INTO transactions 
                (sender_id, receiver_id, amount, status,
                 sender_balance_before, sender_balance_after,
                 receiver_balance_before, receiver_balance_after,
                 note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sender_id, receiver_id, amount, "FAILED",
                sender_balance_before, sender_balance_before,
                receiver_balance_before, receiver_balance_before,
                "Insufficient balance"
            ))
            print("#Debug B-6# time:")
            # conn.commit()
            return False, error_data
            
        print("#Debug B-7# time:")
        # Update balance
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, sender_id)
        )
        print("#Debug B-8# time:")
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, receiver_id)
        )
        
        print("#Debug B-9# time:")
        # Get the balance after transfer
        cursor.execute(
            "SELECT account_id, balance FROM accounts WHERE account_id IN (%s, %s)",
            (sender_id, receiver_id)
        )
        updated_accounts = {row['account_id']: row['balance'] for row in cursor.fetchall()}
        
        sender_balance_after = updated_accounts.get(sender_id)
        receiver_balance_after = updated_accounts.get(receiver_id)
        
        print("#Debug B-10# time:")
        # Record transaction
        cursor.execute("""
            INSERT INTO transactions 
            (sender_id, receiver_id, amount, status,
             sender_balance_before, sender_balance_after,
             receiver_balance_before, receiver_balance_after,
             note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            sender_id, receiver_id, amount, "SUCCESS",
            sender_balance_before, sender_balance_after,
            receiver_balance_before, receiver_balance_after,
            None
        ))
        
        print("#Debug B-11# time:")
        log_transaction(
            sender_id, receiver_id, amount, "SUCCESS",
            sender_balance_before, receiver_balance_before,
            sender_balance_after, receiver_balance_after,
            None,
            elapsed_seconds
        )
        print("#Debug B-11-2# time:")
        # conn.commit()
        return True, "Transfer successful"
        
    except Exception as e:
        print("#Debug B-12# time:")
        # Insert error transaction record
        try:
            print("#Debug B-13# time:")
            cursor.execute("""
                INSERT INTO transactions 
                (sender_id, receiver_id, amount, status,
                 sender_balance_before, sender_balance_after,
                 receiver_balance_before, receiver_balance_after,
                 note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sender_id, receiver_id, amount, "ERROR",
                sender_balance_before, sender_balance_before,
                receiver_balance_before, receiver_balance_before,
                str(e)[:200]
            ))
            # conn.commit()
        except:
            print("#Debug B-14# time:")
            pass  # Ignore error when inserting error record
        log_error(f"Transfer failed: {str(e)}")
        print("#Debug B-15# time:")
        return False, f"Transfer failed: {str(e)}" 
        