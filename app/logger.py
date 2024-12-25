import logging
from config.config import LOG_CONFIG

def setup_logger():
    logging.basicConfig(
        filename=LOG_CONFIG["filename"],
        format=LOG_CONFIG["format"],
        datefmt=LOG_CONFIG["datefmt"],
        level=logging.INFO
    )

def log_transaction(sender_id, receiver_id, amount, status, reason=None):
    message = f"交易 {status}: 发送方={sender_id}, 接收方={receiver_id}, 金额={amount:.2f}"
    if reason:
        message += f" - 原因: {reason}"
    logging.info(message)

def log_error(message):
    logging.error(message) 