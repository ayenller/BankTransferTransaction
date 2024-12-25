# 银行转账命令行应用程序

这是一个基于 Python 的银行转账命令行应用程序，使用 TiDB 作为数据库存储。

## 项目结构
```
bank_transfer_cli/
├── database/
│   ├── init_db.py         # 数据库初始化和建表脚本
│   ├── seed_data.py       # 预埋数据生成脚本
│   └── db_connection.py   # 数据库连接管理
├── app/
│   ├── main.py            # 程序入口，转账交易执行
│   ├── transfer.py        # 转账操作逻辑
│   └── logger.py          # 日志管理
├── config/
│   └── config.py          # 配置文件
├── run_transfers.py       # 转账交易运行脚本
├── requirements.txt       # Python 依赖包
└── README.md              # 项目说明文件
+
```

## 环境要求

- Python 3.8+
- TiDB 数据库
- pip 包管理工具

## 快速开始

### 1. 安装依赖包

首先创建并激活虚拟环境（推荐）：
```bash
# 创建虚拟环境
python -m venv myenv

# 激活虚拟环境
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate
```

安装所需依赖：
```bash
pip install -r requirements.txt
```

### 2. 配置数据库连接

修改 `config/config.py` 文件中的数据库连接参数：
```python
DATABASE_CONFIG = {
    "host": "127.0.0.1",  # 修改为你的 TiDB 主机地址
    "port": 4000,         # TiDB 端口
    "user": "root",       # 数据库用户名
    "database": "banking_system"  # 数据库名称
}
```

### 3. 初始化数据库

运行以下命令创建数据库和表结构：
```bash
python database/init_db.py
```

这将创建：
- banking_system 数据库
- accounts 表（存储账户信息）
- transactions 表（存储交易记录）

### 4. 生成测试数据

运行以下命令生成测试数据：
```bash
python database/seed_data.py
```

这将：
- 创建 100 个测试账户
- 生成 100 条随机交易记录
- 为每个账户设置随机初始余额

### 5. 执行转账交易

运行以下命令执行 10 笔随机转账交易：
```bash
python run_transfers.py
```

每笔转账将显示：
- 转账双方的账户信息
- 转账金额（10-1000元之间的10的倍数）
- 转账前后的账户余额
- 转账结果

### 日志记录

所有转账操作都会记录在 `bank_transfer.log` 文件中，包括：
- 精确到毫秒的转账时间
- 转账状态（成功/失败）
- 转账双方的用户名
- 转账金额（100-1000之间的100的倍数）
- 转账双方的余额变更记录

日志格式示例：
```
[2024-03-21 15:30:45.123] INFO: 交易 SUCCESS: 发送方=user_05(余额: 5000.00->4500.00), 接收方=user_12(余额: 3000.00->3500.00), 金额=500.00
[2024-03-21 15:30:46.456] INFO: 交易 FAILURE: 发送方=user_08(余额: 100.00->100.00), 接收方=user_03(余额: 2000.00->2000.00), 金额=800.00 - 原因: 余额不足
```

## 数据一致性验证

系统使用事务确保每笔转账的原子性，可以通过以下 SQL 在任意时刻验证系统的数据一致性：

```sql
-- 查询系统总余额
SELECT SUM(balance) as total_balance FROM banking_system.accounts;
```

由于每笔转账都是在同一个事务中完成转出和转入操作，因此：
1. 系统总余额在任意时刻都应该保持不变
2. 总余额等于所有账户初始余额之和
3. 失败的转账不会影响系统总余额

可以通过以下 SQL 查看转账历史和余额变化：

```sql
-- 查看成功的转账记录
SELECT t.*, 
       a1.account_name as sender_name, 
       a2.account_name as receiver_name
FROM banking_system.transactions t
JOIN banking_system.accounts a1 ON t.sender_id = a1.account_id
JOIN banking_system.accounts a2 ON t.receiver_id = a2.account_id
WHERE t.status = 'SUCCESS'
ORDER BY t.created_at DESC
LIMIT 10;

-- 查看账户余额变化
SELECT account_name, balance
FROM banking_system.accounts
ORDER BY account_id
LIMIT 10;
```

验证步骤：
1. 在开始转账测试前记录总余额
2. 在转账过程中随时可以查询总余额，应与初始值相同
3. 在所有转账完成后，再次验证总余额

## 注意事项

1. 确保 TiDB 数据库已启动并可访问
2. 账户余额不足时转账将失败
3. 所有转账操作都在事务中执行，确保数据一致性
4. 每笔转账都会实时记录到日志文件，便于追踪和审计
5. 可以通过系统总余额验证数据一致性
