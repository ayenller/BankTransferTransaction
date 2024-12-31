def format_transfer_line(time, status, sender="N/A", receiver="N/A", amount="0.00",
                        sender_before="0.00", sender_after="0.00",
                        receiver_before="0.00", receiver_after="0.00", note=""):
    """
    Format a transfer status line with consistent layout
    
    Args:
        time: Current time in seconds
        status: Transaction status
        sender: Sender account name
        receiver: Receiver account name
        amount: Transfer amount
        sender_before: Sender balance before transfer
        sender_after: Sender balance after transfer
        receiver_before: Receiver balance before transfer
        receiver_after: Receiver balance after transfer
        note: Additional note or error message
        
    Returns:
        str: Formatted status line
    """
    return (f"{time:>3}s   {status:<11} {sender:<18} {receiver:<18} "
            f"{amount:>8} USD    "
            f"{sender_before:>8.2f}->{sender_after:<8.2f}    "
            f"{receiver_before:>8.2f}->{receiver_after:<8.2f}    "
            f"{note}")

def print_transfer_header():
    """Print the transfer status table header"""
    print("\nStarting transfer transactions...")
    print("-" * 150)
    print("Time   Status   Sender             Receiver             Amount         Sender Balance        Receiver Balance     Note")
    print("-" * 150) 