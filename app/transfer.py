from decimal import Decimal
from app.logger import log_transaction, log_error

def transfer_amount(sender_id, receiver_id, amount, cursor, conn):
    try:
        # 检查发送方余额
        cursor.execute(
            "SELECT balance FROM accounts WHERE account_id = %s FOR UPDATE",
            (sender_id,)
        )
        sender_balance = cursor.fetchone()
        
        if not sender_balance or sender_balance['balance'] < amount:
            log_transaction(sender_id, receiver_id, amount, "FAILURE", "余额不足")
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
        
        # 记录交易
        cursor.execute("""
            INSERT INTO transactions (sender_id, receiver_id, amount, status)
            VALUES (%s, %s, %s, %s)
        """, (sender_id, receiver_id, amount, "SUCCESS"))
        
        log_transaction(sender_id, receiver_id, amount, "SUCCESS")
        return True, "转账成功"
        
    except Exception as e:
        log_error(f"转账失败: {str(e)}")
        return False, f"转账失败: {str(e)}" 