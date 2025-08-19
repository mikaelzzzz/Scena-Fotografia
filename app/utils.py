import re


def normalize_whatsapp(raw_value: str) -> str:
    """Normalize a WhatsApp/phone string to digits with Brazil country code 55.

    Examples:
    - "+55 (11) 99999-9999" -> "5511999999999"
    - "11 99999-9999" -> "5511999999999"
    - "(31) 8888-8888" -> "553188888888"
    - "00999..." -> "55" + stripped leading zeros
    """
    digits = re.sub(r"\D+", "", raw_value or "")

    if not digits:
        return ""

    if digits.startswith("55"):
        normalized = digits
    else:
        digits_no_zero = digits.lstrip("0") or "0"
        if len(digits_no_zero) in {10, 11}:
            normalized = f"55{digits_no_zero}"
        else:
            normalized = digits_no_zero if digits_no_zero.startswith("55") else f"55{digits_no_zero}"

    return normalized


def whatsapp_link(normalized_digits: str) -> str:
    return f"https://wa.me/{normalized_digits}"
