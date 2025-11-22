import logging
from typing import Dict
import requests
from core.schemas import Derivatives
from core.retry import retry
from core.time_utils import now_ms

logger = logging.getLogger(__name__)


class DerivativesClient:
    BASE_URL = "https://www.okx.com/api/v5"

    @retry((requests.RequestException,), tries=3, delay=1, backoff=2)
    def fetch(self, inst_id: str) -> Derivatives:
        url = f"{self.BASE_URL}/public/funding-rate"
        params = {"instId": inst_id}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [{}])[0]
        oi_resp = requests.get(
            f"{self.BASE_URL}/public/open-interest", params={"instId": inst_id}, timeout=10
        )
        oi_resp.raise_for_status()
        oi_data = oi_resp.json().get("data", [{}])[0]
        ts = int(data.get("fundingTime", now_ms()))
        return Derivatives(
            ts=ts,
            instId=inst_id,
            open_interest=float(oi_data.get("oi", 0.0)),
            funding_rate=float(data.get("fundingRate", 0.0)),
            source="OKX",
        )
