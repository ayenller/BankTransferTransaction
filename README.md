# Bank Transfer CLI Application

A Python-based command-line application for bank transfers using TiDB as the database storage.

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
├── config/
│   ├── __init__.py
│   └── config.py         # Configuration settings
├── run_transfers.py      # CLI entry point
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

## Requirements

- Python 3.8+
- TiDB/MySQL
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
Time   Status   Sender             Receiver             Amount         Sender Balance        Receiver Balance     Note
----------------------------------------------------------------------------------------------------------------------------------
  1s   SUCCESS  user_74            user_15              900.00 USD    4400.00->3500.00    2600.00->3500.00    
  2s   FAILED   user_32            user_89              700.00 USD    1200.00->1200.00    3800.00->3800.00    Insufficient balance
```

### Transaction States

- `SUCCESS`: Transfer completed successfully
- `FAILED`: Transfer failed (e.g., insufficient balance)
- `ERROR`: System error occurred
- `WAIT`: Waiting for next transaction

## Configuration

Configuration settings in `config/config.py`:

- `DATABASE_CONFIG`: Production database settings
- `TEST_DATABASE_CONFIG`: Initialize data connection
- `LOG_CONFIG`: Logging configuration

## Development

### Test Environment

Use test database for Initialize data:
```python
with get_cursor(config_type="test") as (cursor, conn):
    # Development code here
```

### Code Style

The project uses:
- black for code formatting
- flake8 for code checking
- isort for import sorting

## Logging

All operations are logged in `bank_transfer.log`:
- Transfer details
- Balance changes
- Error messages

Log format:
```
[2024-03-21 15:30:45.123] INFO: Transaction SUCCESS: Sender=user_05(Balance: 5000.00->4500.00), Receiver=user_12(Balance: 3000.00->3500.00), Amount=500.00
```

## Error Handling

The application handles:
- Insufficient balance
- Database connection issues
- Concurrent transaction conflicts
- System errors

## Verify the data consistency by executing the following sql any time.
```
-- View account balances
SELECT account_name, balance
FROM banking_system.accounts
ORDER BY account_id
LIMIT 10;
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the APACHE2.0 License.
