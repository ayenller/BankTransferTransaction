import os
import sys
import random
from decimal import Decimal

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from database.db_connection import get_cursor

def seed_accounts(cursor, num_accounts=100):
    """初始化账户数据"""
    print("开始初始化账户数据...")
    
    # 准备批量插入的数据
    accounts_data = []
    for i in range(num_accounts):
        account = (
            f"用户_{i+1}",  # account_name
            Decimal(str(random.uniform(1000.00, 10000.00))).quantize(Decimal('0.00'))  # balance
        )
        accounts_data.append(account)
    
    # 批量插入账户数据
    cursor.executemany(
        """
        INSERT INTO banking_system.accounts (account_name, balance)
        VALUES (%s, %s)
        """,
        accounts_data
    )
    
    print(f"成功创建 {num_accounts} 个账户")

def seed_transactions(cursor, num_transactions=100):
    """初始化交易记录"""
    print("开始初始化交易记录...")
    
    # 获取所有账户ID
    cursor.execute("SELECT account_id FROM banking_system.accounts")
    account_ids = [row['account_id'] for row in cursor.fetchall()]
    
    if len(account_ids) < 2:
        print("账户数量不足，无法创建交易记录")
        return
    
    # 准备批量插入的数据
    transactions_data = []
    for _ in range(num_transactions):
        # 随机选择发送方和接收方
        sender_id, receiver_id = random.sample(account_ids, 2)
        
        transaction = (
            sender_id,  # sender_id
            receiver_id,  # receiver_id
            Decimal(str(random.uniform(10.00, 1000.00))).quantize(Decimal('0.00')),  # amount
            random.choice(['SUCCESS', 'FAILURE'])  # status
        )
        transactions_data.append(transaction)
    
    # 批量插入交易记录
    cursor.executemany(
        """
        INSERT INTO banking_system.transactions 
        (sender_id, receiver_id, amount, status)
        VALUES (%s, %s, %s, %s)
        """,
        transactions_data
    )
    
    print(f"成功创建 {num_transactions} 条交易记录")

def main():
    try:
        with get_cursor() as (cursor, conn):
            # 检查数据库是否存在
            cursor.execute("USE banking_system")
            
            # 按照正确的顺序清空表（先删除有外键约束的表）
            cursor.execute("DELETE FROM banking_system.transactions")
            cursor.execute("DELETE FROM banking_system.accounts")
            
            # 初始化数据
            seed_accounts(cursor)
            seed_transactions(cursor)
            
            print("数据初始化完成！")
            
            # 显示一些统计信息
            cursor.execute("SELECT COUNT(*) as count FROM banking_system.accounts")
            accounts_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM banking_system.transactions")
            transactions_count = cursor.fetchone()['count']
            
            print(f"\n统计信息:")
            print(f"账户总数: {accounts_count}")
            print(f"交易记录总数: {transactions_count}")
            
    except Exception as e:
        print(f"数据初始化失败: {str(e)}")

if __name__ == "__main__":
    main() 