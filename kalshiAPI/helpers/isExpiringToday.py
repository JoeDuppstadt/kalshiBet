from typing import  Optional
from datetime import datetime, timezone, timedelta


def is_expiring_today(expiration_str: Optional[str]) -> bool:
    """
    Returns True if the expiration timestamp is considered "today" in a practical sense:
    - Either on the current UTC date, OR
    - In the first 6 hours of the next UTC date (i.e. up to 06:00 UTC the next day)

    This is useful for systems where "today's" items can expire shortly into the next day.
    """
    if not expiration_str:
        return False

    try:
        # Parse ISO 8601 string → aware datetime
        # Handles both Z and ±00:00 style
        dt = datetime.fromisoformat(expiration_str.replace("Z", "+00:00"))

        # Current time in UTC
        now_utc = datetime.now(timezone.utc)

        # Start of today (00:00 UTC)
        today_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)

        # Cutoff = tomorrow 06:00 UTC
        cutoff = today_start + timedelta(days=1, hours=6)

        # Expires "today" if it's between today 00:00 and tomorrow 06:00
        return today_start <= dt < cutoff

    except (ValueError, TypeError):
        return False