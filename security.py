import re
from typing import Tuple

class SecurityValidator:
    """Guard against obvious code-/SQL-injection patterns in free-text."""

    SUSPICIOUS_PATTERNS = [
        r'<script.*?>.*?</script>', r'javascript:', r'on\w+\s*=',
        r'eval\s*\(', r'exec\s*\(', r'import\s+os', r'__import__',
        r'subprocess', r'system\(', r'rm\s+-rf', r'DROP\s+TABLE',
        r'DELETE\s+FROM', r'INSERT\s+INTO', r'UPDATE\s+.*SET',
    ]

    @classmethod
    def is_safe(cls, text: str) -> Tuple[bool, str]:
        if not text or not isinstance(text, str):
            return True, ""
        lowered = text.lower()
        for pat in cls.SUSPICIOUS_PATTERNS:
            if re.search(pat, lowered, re.IGNORECASE):
                return False, f"Potentially malicious content detected: {pat}"
        return True, ""
