# Bank Transfer CLI Application

A Python-based command-line application for bank transfers using TiDB as the database storage.

## Project Structure
```
bank_transfer_cli/
├── database/
│   ├── init_db.py         # Database initialization and table creation
│   ├── seed_data.py       # Test data generation
│   └── db_connection.py   # Database connection management
├── app/
│   ├── main.py            # Main entry, transfer execution
│   ├── transfer.py        # Transfer logic
│   └── logger.py          # Logging management
├── config/
│   └── config.py          # Configuration file
├── run_transfers.py       # Transfer execution script
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Requirements

- Python 3.8+
- TiDB database
- pip package management tool

## Quick Start

### 1. Install Dependencies

First, create and activate a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate
```

Install required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Database Connection

Modify database connection parameters in `config/config.py`:
```python
DATABASE_CONFIG = {
    "host": "127.0.0.1",  # Your TiDB host address
    "port": 4000,         # TiDB port
    "user": "root",       # Database username
    "database": "banking_system"  # Database name
}
```

### 3. Initialize Database

Run the following command to create database and tables:
```bash
python database/init_db.py
```

This will create:
- banking_system database
- accounts table (stores account information)
- transactions table (stores transaction records)

### 4. Generate Test Data

Run the following command to generate test data:
```bash
python database/seed_data.py
```

This will:
- Create 100 test accounts
- Generate 100 random transaction records
- Set random initial balances for each account

### 5. Execute Transfers

Run the following command to execute random transfers:
```bash
python run_transfers.py
```

Each transfer will display:
- Account information for both parties
- Transfer amount (between 100-1000 USD, multiples of 100)
- Account balances before and after transfer
- Transfer result

### Logging

All transfer operations are logged in `bank_transfer.log`, including:
- Transfer time (millisecond precision)
- Transfer status (SUCCESS/FAILED)
- Usernames of both parties
- Transfer amount (between 100-1000 USD, multiples of 100)
- Balance changes for both parties

Log format example:
```
[2024-03-21 15:30:45.123] INFO: Transaction SUCCESS: Sender=user_05(Balance: 5000.00->4500.00), Receiver=user_12(Balance: 3000.00->3500.00), Amount=500.00
[2024-03-21 15:30:46.456] INFO: Transaction FAILED: Sender=user_08(Balance: 100.00->100.00), Receiver=user_03(Balance: 2000.00->2000.00), Amount=800.00 - Reason: Insufficient balance
```

## Data Consistency Verification

The system uses transactions to ensure atomicity of each transfer. You can verify system data consistency at any time using the following SQL:

```sql
-- Query total system balance
SELECT SUM(balance) as total_balance FROM banking_system.accounts;
```

Since each transfer completes both debit and credit operations in a single transaction:
1. Total system balance should remain constant at all times
2. Total balance equals the sum of all initial account balances
3. Failed transfers do not affect the system total balance

You can view transfer history and balance changes using these SQL queries:

```sql
-- View successful transfers
SELECT t.*, 
       a1.account_name as sender_name, 
       a2.account_name as receiver_name
FROM banking_system.transactions t
JOIN banking_system.accounts a1 ON t.sender_id = a1.account_id
JOIN banking_system.accounts a2 ON t.receiver_id = a2.account_id
WHERE t.status = 'SUCCESS'
ORDER BY t.created_at DESC
LIMIT 10;

-- View account balances
SELECT account_name, balance
FROM banking_system.accounts
ORDER BY account_id
LIMIT 10;
```

Verification steps:
1. Record total balance before starting transfer tests
2. Query total balance during transfers - should match initial value
3. Verify total balance again after all transfers complete

## Notes

1. Ensure TiDB database is running and accessible
2. Transfers will fail if account balance is insufficient
3. All transfer operations execute within transactions to ensure data consistency
4. Each transfer is logged in real-time for tracking and auditing
5. System consistency can be verified through total balance checks
