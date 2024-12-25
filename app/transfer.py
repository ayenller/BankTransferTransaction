from decimal import Decimal
from app.logger import log_transaction, log_error

def transfer_amount(sender_id, receiver_id, amount, cursor, conn):
    try:
        # 检查发送方余额
        cursor.execute(
            "SELECT account_id, balance FROM accounts WHERE account_id IN (%s, %s) FOR UPDATE",
            (sender_id, receiver_id)
        )
        accounts = {row['account_id']: row['balance'] for row in cursor.fetchall()}
        
        sender_balance_before = accounts.get(sender_id, 0)
        receiver_balance_before = accounts.get(receiver_id, 0)
        
        if not sender_balance_before or sender_balance_before < amount:
            log_transaction(
                sender_id, receiver_id, amount, "FAILURE",
                sender_balance_before, receiver_balance_before,
                sender_balance_before, receiver_balance_before,
                "余额不足"
            )
            return False, "余额不足"
            
        # 更新账户余额
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_id = %s",
            (amount, sender_id)
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_id = %s",
            (amount, receiver_id)
        )
        
        # 获取更新后的余额
        cursor.execute(
            "SELECT account_id, balance FROM accounts WHERE account_id IN (%s, %s)",
            (sender_id, receiver_id)
        )
        updated_accounts = {row['account_id']: row['balance'] for row in cursor.fetchall()}
        
        sender_balance_after = updated_accounts.get(sender_id)
        receiver_balance_after = updated_accounts.get(receiver_id)
        
        # 记录交易
        cursor.execute("""
            INSERT INTO transactions (sender_id, receiver_id, amount, status)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, receiver_id, amount, "SUCCESS"))
        
        log_transaction(
            sender_id, receiver_id, amount, "SUCCESS",
            sender_balance_before, receiver_balance_before,
            sender_balance_after, receiver_balance_after
        )
        return True, "转账成功"
        
    except Exception as e:
        log_error(f"转账失败: {str(e)}")
        return False, f"转账失败: {str(e)}" 