import logging
from datetime import datetime
from config.config import LOG_CONFIG

def setup_logger():
    logging.basicConfig(
        filename=LOG_CONFIG["filename"],
        format=LOG_CONFIG["format"],
        datefmt=LOG_CONFIG["datefmt"],
        level=logging.INFO
    )

def log_transaction(sender_id, receiver_id, amount, status, sender_balance_before=None, 
                   receiver_balance_before=None, sender_balance_after=None, 
                   receiver_balance_after=None, reason=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (f"Transaction {status}: "
              f"Sender={sender_id}(Balance: {sender_balance_before:.2f}->{sender_balance_after:.2f}), "
              f"Receiver={receiver_id}(Balance: {receiver_balance_before:.2f}->{receiver_balance_after:.2f}), "
              f"Amount={amount:.2f}")
    if reason:
        message += f" - Reason: {reason}"
    logging.info(f"[{current_time}] {message}")

def log_error(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.error(f"[{current_time}] {message}") 