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
- 转账时间
- 转账金额
- 转账状态
- 错误信息（如果有）

## 数据库表结构

### accounts 表
```sql
CREATE TABLE accounts (
    account_id BIGINT AUTO_RANDOM,
    account_name VARCHAR(100) NOT NULL DEFAULT '',
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (account_id)
);
```

### transactions 表
```sql
CREATE TABLE transactions (
    transaction_id BIGINT AUTO_RANDOM,
    sender_id BIGINT NOT NULL,
    receiver_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (sender_id) REFERENCES accounts(account_id),
    FOREIGN KEY (receiver_id) REFERENCES accounts(account_id)
);
```

## 注意事项

1. 确保 TiDB 数据库已启动并可访问
2. 转账金额必须是 10 的倍数
3. 账户余额不足时转账将失败
4. 所有转账操作都在事务中执行，确保数据一致性
