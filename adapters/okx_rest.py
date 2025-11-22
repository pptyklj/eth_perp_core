import logging
from typing import List
import requests
from core.schemas import Candle
from core.retry import retry

logger = logging.getLogger(__name__)


class OKXRestClient:
    BASE_URL = "https://www.okx.com/api/v5"

    @retry((requests.RequestException,), tries=3, delay=1, backoff=2)
    def fetch_candles(self, inst_id: str, bar: str, limit: int) -> List[Candle]:
        url = f"{self.BASE_URL}/market/candles"
        params = {"instId": inst_id, "bar": bar, "limit": limit}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
        candles: List[Candle] = []
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
