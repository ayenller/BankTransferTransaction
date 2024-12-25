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
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    message = (f"交易 {status}: "
              f"发送方={sender_id}(余额: {sender_balance_before:.2f}->{sender_balance_after:.2f}), "
              f"接收方={receiver_id}(余额: {receiver_balance_before:.2f}->{receiver_balance_after:.2f}), "
              f"金额={amount:.2f}")
    if reason:
        message += f" - 原因: {reason}"
    logging.info(f"[{current_time}] {message}")

def log_error(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    logging.error(f"[{current_time}] {message}") 