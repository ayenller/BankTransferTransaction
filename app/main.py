import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import random
from decimal import Decimal

from database.db_connection import get_cursor
from app.transfer import transfer_amount
from app.logger import setup_logger

def execute_random_transfers(num_transfers=10):
    """执行随机转账交易"""
    setup_logger()
    
    # 只在第一次调用时打印表头
    if not hasattr(execute_random_transfers, 'header_printed'):
        print("\n开始执行转账交易...")
        print("-" * 100)
        print("时间                        交易状态    发送方              接收方              金额        发送方余额变更              转出方余额变更")
        print("-" * 100)
        execute_random_transfers.header_printed = True
    
    try:
        with get_cursor() as (cursor, conn):
            # 获取所有账户信息
            cursor.execute("""
                SELECT account_id, account_name, balance 
                FROM banking_system.accounts
            """)
            accounts = cursor.fetchall()
            
            if len(accounts) < 2:
                print("账户数量不足，无法执行转账")
                return
            
            successful_transfers = 0
            failed_transfers = 0
            
            for i in range(num_transfers):
                # 随机选择转出和转入账户
                sender, receiver = random.sample(accounts, 2)
                # 随机生成转账金额（100-1000之间，且为100的倍数）
                amount = Decimal(str(random.randrange(1, 11) * 100)).quantize(Decimal('0.00'))
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # 执行转账
                success, message = transfer_amount(
                    sender['account_id'],
                    receiver['account_id'],
                    amount,
                    cursor,
                    conn
                )
                
                # 获取转账后的余额
                if success:
                    cursor.execute("""
                        SELECT account_name, balance 
                        FROM banking_system.accounts 
                        WHERE account_id IN (%s, %s)
                    """, (sender['account_id'], receiver['account_id']))
                    updated_balances = cursor.fetchall()
                    
                    status = "成功"
                    sender_balance_after = updated_balances[0]['balance']
                    receiver_balance_after = updated_balances[1]['balance']
                else:
                    status = "失败"
                    sender_balance_after = sender['balance']
                    receiver_balance_after = receiver['balance']
                
                # 单行格式输出
                print(f"{current_time}  {status:<8} {sender['account_name']:<18} {receiver['account_name']:<18} "
                      f"{amount:>8.2f} 元  "
                      f"{sender['balance']:>8.2f}->{sender_balance_after:<8.2f} "
                      f"{receiver['balance']:>8.2f}->{receiver_balance_after:<8.2f}")
                
                if success:
                    successful_transfers += 1
                else:
                    failed_transfers += 1
            
    except Exception as e:
        print(f"执行转账时发生错误: {str(e)}")

if __name__ == "__main__":
    execute_random_transfers(10) 