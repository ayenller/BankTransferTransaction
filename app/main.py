import os
import sys

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
            
            print("\n开始执行转账交易...")
            print("-" * 50)
            
            for i in range(num_transfers):
                # 随机选择转出和转入账户
                sender, receiver = random.sample(accounts, 2)
                # 随机生成转账金额（10-1000之间，且为10的倍数）
                amount = Decimal(str(random.randrange(1, 101) * 10)).quantize(Decimal('0.00'))
                
                print(f"\n转账 #{i+1}:")
                print(f"转账详情:")
                print(f"  发送方: {sender['account_name']}(ID:{sender['account_id']})")
                print(f"  接收方: {receiver['account_name']}(ID:{receiver['account_id']})")
                print(f"  转账金额: {amount} 元")
                print(f"  转账前余额:")
                print(f"    {sender['account_name']}: {sender['balance']} 元")
                print(f"    {receiver['account_name']}: {receiver['balance']} 元")
                
                # 执行转账
                success, message = transfer_amount(
                    sender['account_id'],
                    receiver['account_id'],
                    amount,
                    cursor,
                    conn
                )
                
                print(f"转账结果: {message}")
                
                # 获取转账后的余额
                if success:
                    cursor.execute("""
                        SELECT account_name, balance 
                        FROM banking_system.accounts 
                        WHERE account_id IN (%s, %s)
                    """, (sender['account_id'], receiver['account_id']))
                    updated_balances = cursor.fetchall()
                    
                    print(f"  转账后余额:")
                    for account in updated_balances:
                        print(f"    {account['account_name']}: {account['balance']} 元")
                    
                    # 更新本地账户数据，用于下一次转账
                    for account in accounts:
                        if account['account_id'] == sender['account_id']:
                            account['balance'] = updated_balances[0]['balance']
                        elif account['account_id'] == receiver['account_id']:
                            account['balance'] = updated_balances[1]['balance']
                
                if success:
                    successful_transfers += 1
                else:
                    failed_transfers += 1
            
            print("\n" + "=" * 50)
            print(f"转账统计:")
            print(f"总计执行: {num_transfers} 笔")
            print(f"成功: {successful_transfers} 笔")
            print(f"失败: {failed_transfers} 笔")
            
            # 显示所有账户的当前余额
            print("\n当前账户余额:")
            print("-" * 50)
            cursor.execute("""
                SELECT account_name, balance 
                FROM banking_system.accounts 
                ORDER BY account_id
                LIMIT 5
            """)
            for account in cursor.fetchall():
                print(f"{account['account_name']}: {account['balance']} 元")
            print("... (更多账户省略)")
            
    except Exception as e:
        print(f"执行转账时发生错误: {str(e)}")

if __name__ == "__main__":
    execute_random_transfers(10) 