import logging
from typing import Dict, List
import requests
import pandas as pd
from core.schemas import Candle
from core.retry import retry

logger = logging.getLogger(__name__)


class OKXRestAdapter:
    BASE_URL = "https://www.okx.com/api/v5"

    @retry((requests.RequestException,), tries=3, delay=1, backoff=2)
    def fetch_candles(self, inst_id: str, bar: str, limit: int) -> List[Candle]:
        url = f"{self.BASE_URL}/market/candles"
        params = {"instId": inst_id, "bar": bar, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        candles = []
        for item in data:
            ts, o, h, l, c, vol, *_ = item
            candles.append(
                Candle(
                    ts=int(ts),
                    open=float(o),
                    high=float(h),
                    low=float(l),
                    close=float(c),
                    volume=float(vol),
                    confirm=1,
                    is_filled=True,
                )
            )
        candles.sort(key=lambda x: x.ts)
        return candles


def warmup_candles(config: Dict) -> Dict[str, List[Candle]]:
    inst_id = config.get("instId")
    warmup_conf = config.get("warmup", {})
    adapter = OKXRestAdapter()
    result: Dict[str, List[Candle]] = {}
    for bar, limit in warmup_conf.items():
        try:
            candles = adapter.fetch_candles(inst_id, bar, limit)
            result[bar] = candles
            logger.info("Warmup fetched %s candles for %s", len(candles), bar)
        except Exception as exc:  # pragma: no cover - network failure
            logger.error("Warmup failed for %s: %s", bar, exc)
            result[bar] = []
    return result
