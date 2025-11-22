import time
from datetime import datetime, timezone


def now_ms() -> int:
    return int(time.time() * 1000)


def ts_to_iso(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).isoformat()
