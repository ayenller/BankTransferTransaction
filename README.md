# Bank Transfer CLI Application

A Python-based command-line application for simulating bank transfers using TiDB as the database storage.

## Features

- Real-time transfer execution and monitoring
- Concurrent transfer processing with multi-threading
- Live transaction status display
- Automatic database reconnection
- Comprehensive error handling
- Transaction logging
- Support for test and production environments

## Project Structure
```
bank_transfer_cli/
├── database/
│   ├── __init__.py
│   ├── init_db.py         # Database initialization
│   ├── seed_data.py       # Test data generation
│   └── db_connection.py   # Database connection management
├── app/
│   ├── __init__.py
│   ├── main.py           # Main application logic
│   ├── transfer.py       # Transfer execution logic
│   └── logger.py         # Logging utilities
├── utils/
│   ├── __init__.py
│   ├── format_utils.py   # Output formatting utilities
│   └── queue_utils.py    # Queue management utilities
├── config/
│   ├── __init__.py
│   └── config.py         # Configuration settings
├── run_transfers.py      # CLI entry point
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

## Requirements

- Python 3.8+
- TiDB 6.0+
- Dependencies listed in requirements.txt

## Installation

1. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Setup

1. Initialize the database structure:
```bash
python database/init_db.py
```

2. Generate test data:
```bash
python database/seed_data.py
```

This will:
- Create required database and tables
- Generate 100 test accounts
- Set random initial balances

## Usage

### Running Transfers

Execute transfers for a specified duration:
```bash
python run_transfers.py <duration_minutes>

# Example: Run for 5 minutes
python run_transfers.py 5
```

### Output Format

The application displays real-time transfer status:
```
Time   Status       Sender   Receiver   Amount        Sender Balance        Receiver Balance     Note
----------------------------------------------------------------------------------------------------------------------------------------------------------------
  1s   SUCCESS      user_74  user_15     900.00 USD    4400.00->3500.00      2600.00->3500.00    
  2s   FAILED       user_79  user_27     200.00 USD    8100.00->8100.00      6100.00->6100.00     Insufficient balance
  3s   BUSI_ERROR   N/A      N/A         0.00 USD      0.00->0.00            0.00->0.00           Insufficient accounts to perform transfers
  4s   DB_RETRY     N/A      N/A         0.00 USD      0.00->0.00            0.00->0.00           Retry 1/3000: 2003 (HY000): Can't connect to MySQL...
  5s   DB_RETRY     N/A      N/A         0.00 USD      0.00->0.00            0.00->0.00           Retry 29/3000: 1049 (42000): Unknown database 'banking_system'  
  6s   DB_RECOVERE  N/A      N/A         0.00 USD      0.00->0.00            0.00->0.00           Database connection restored
  7s   BUSI_ERROR   N/A      N/A         0.00 USD      0.00->0.00            0.00->0.00           Insufficient accounts to perform transfers
  8s   WAIT         N/A      N/A         0.00 USD      0.00->0.00            0.00->0.00           Waiting for transaction...
```

### Transaction States

- `SUCCESS`: Transfer completed successfully
- `FAILED`: Insufficient balance for the sender account
- `BUSI_ERROR`: Insufficient accounts to perform transfers, accounts number less than 2
- `DB_RETRY`: Database reconnection attempt, or database `banking_system` not found.
- `DB_RECOVERE`: Database `banking_system` connection restored
- `WAIT`: Waiting for next transaction input

## Configuration

Configuration settings in `config/config.py`:

- `DATABASE_CONFIG`: Production database settings
- `TEST_DATABASE_CONFIG`: Test database settings
- `LOG_CONFIG`: Logging configuration

## Development

### Error Handling

The application handles:
- Database connection issues with automatic retry
- Business logic errors (e.g., insufficient balance)
- Concurrent transaction conflicts
- System errors

### Logging

All operations are logged in `bank_transfer.log`:
```
[2024-03-21 15:30:45.123] INFO: Transaction SUCCESS: Sender=user_05(Balance: 5000.00->4500.00), Receiver=user_12(Balance: 3000.00->3500.00), Amount=500.00
[2024-03-21 15:30:46.234] ERROR: Database connection attempt 1 failed: Connection refused
```

## Data Verification

Check data consistency using SQL:
```sql
-- View account balances
SELECT account_name, balance
FROM banking_system.accounts
ORDER BY account_id
LIMIT 10;

-- View recent transactions
SELECT * FROM banking_system.transactions
ORDER BY created_at DESC
LIMIT 5;
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
