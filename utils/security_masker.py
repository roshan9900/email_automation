import re

def mask_account_number(account_number: str) -> str:
    """
    Masks account number keeping only last 4 digits visible.
    Example: 1234567890 -> XXXX7890
    """
    if not account_number:
        return "XXXX"
    clean = re.sub(r"\D", "", account_number)
    if len(clean) <= 4:
        return f"XXXX{clean}"
    return f"XXXX{clean[-4:]}"

def mask_card_number(card_number: str) -> str:
    """
    Masks credit card number keeping only last 4 digits visible.
    Supports formatted and unformatted cards.
    Example: 4567123456788901 -> XXXX-XXXX-XXXX-8901
    Example: 4567XXXX8901 -> 4567XXXX8901
    Example: 987654321 -> XXXX4321
    """
    if not card_number:
        return "XXXX"
    if "X" in card_number.upper():
        return card_number.upper()
    clean = re.sub(r"\D", "", card_number)
    if len(clean) >= 12:
        return f"XXXX-XXXX-XXXX-{clean[-4:]}"
    elif len(clean) > 4:
        return f"XXXX{clean[-4:]}"
    return f"XXXX{clean}"

def mask_currency(amount: float) -> str:
    """
    Formats amount in Indian Currency format: INR 1,25,000.00
    """
    try:
        s, *d = f"{amount:.2f}".split(".")
        r = []
        if len(s) > 3:
            r.append(s[-3:])
            s = s[:-3]
            while len(s) > 2:
                r.append(s[-2:])
                s = s[:-2]
            if s:
                r.append(s)
            formatted_int = ",".join(reversed(r))
        else:
            formatted_int = s
        return f"INR {formatted_int}"
    except Exception:
        return f"INR {amount:,.2f}"

