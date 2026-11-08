"""
Language Detection & Multilingual Support Module (Section 13 Optional Enhancement)
Identifies customer query language (English, Hindi, Hinglish, Spanish, French, etc.)
and localized handling.
"""
import re
from typing import Dict, Any

# Common indicative vocabulary for multilingual detection
INDICATORS = {
    "Hindi / Hinglish": [
        "namaste", "kripya", "mera", "meri", "khata", "shesh", "balance", 
        "paise", "madad", "bhejo", "chahiye", "karo", "dhanyawad", "aapka",
        "rupaye", "khatabook", "paisa"
    ],
    "Spanish": [
        "hola", "por favor", "saldo", "cuenta", "tarjeta", "gracias",
        "estado de cuenta", "movimientos", "banco"
    ],
    "French": [
        "bonjour", "s'il vous plaît", "solde", "compte", "carte", "relevé",
        "merci", "banque"
    ],
    "German": [
        "hallo", "bitte", "kontostand", "konto", "karte", "danke",
        "kontoauszug"
    ]
}

def detect_language(text: str) -> Dict[str, Any]:
    """
    Detects language of incoming text with fallback to English.
    Checks Devanagari Unicode block and multilingual keyword matches.
    """
    # 1. Check Devanagari script (Hindi Unicode range \u0900-\u097F)
    if re.search(r"[\u0900-\u097F]", text):
        return {
            "language": "Hindi (Devanagari)",
            "code": "hi",
            "is_multilingual": True,
            "confidence": 0.98
        }

    lower_text = text.lower()
    
    # 2. Check vocabulary markers
    for lang_name, markers in INDICATORS.items():
        matches = [m for m in markers if re.search(rf"\b{re.escape(m)}\b", lower_text)]
        if len(matches) >= 2 or (len(matches) >= 1 and ("kripya" in matches or "namaste" in matches or "saldo" in matches or "solde" in matches)):
            code = "hi-latn" if "Hindi" in lang_name else lang_name[:2].lower()
            return {
                "language": lang_name,
                "code": code,
                "is_multilingual": True,
                "matched_markers": matches,
                "confidence": 0.85
            }

    return {
        "language": "English",
        "code": "en",
        "is_multilingual": False,
        "confidence": 0.99
    }

