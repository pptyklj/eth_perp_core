import asyncio
import json
import logging
from pathlib import Path
import yaml
import pandas as pd

from adapters.okx_ws import OKXWebSocket
from adapters.derivatives_okx_or_bybit import DerivativesClient
from core.time_utils import now_ms
from core.schemas import Candle, Derivatives
from indicators.indicator_calc import compute_indicators
from indicators.factor_compress import FactorCompressor
from fusion.fusion_engine import fuse_factors
from fusion.signal_engine import SignalEngine
from report.report_builder import build_report
from notifier.email_sender_qq import send_email
from core.warmup import warmup_candles

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class Runner:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = yaml.safe_load(Path(config_path).read_text())
        self.inst_id = self.config["instId"]
        self.df = pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume"])
        self.deriv_client = DerivativesClient()
        self.compressor = FactorCompressor(rolling_window_days=self.config.get("rolling_window_days", 14))
        self.signal_engine = SignalEngine(
            confirm_n=self.config.get("confirm_n", 2), cooldown_n=self.config.get("cooldown_n", 1)
        )
        self.last_deriv: Derivatives | None = None
        self.last_deriv_poll_ts = 0
        self.last_heartbeat_ts = 0
        self.last_signal = "NEUTRAL"

    def start(self):  # pragma: no cover - integration
        warmup_candles(self.config)
        ws = OKXWebSocket(self.inst_id, self.on_candle)
        ws.start()

    def on_candle(self, candle: Candle):
        if candle.confirm != 1:
            return
        self.append_candle(candle)
        indicators_df = compute_indicators(self.df)
        indicators_row = indicators_df.iloc[-1]
        factors = self.compressor.compute_all(indicators_df, self.last_deriv, self.last_deriv)
        now = now_ms()
        deriv = self.last_deriv
        if now - self.last_deriv_poll_ts >= self.config["polling"]["derivatives_interval_sec"] * 1000:
            deriv = self.deriv_client.fetch(self.inst_id)
            self.last_deriv_poll_ts = now
            self.last_deriv = deriv
        final, threshold, contrib = fuse_factors(
            factors,
            weights=self.config["weights"],
            threshold_k=self.config["threshold_k"],
            volatility=factors.Volatility,
        )
        signal = self.signal_engine.generate(final, threshold)
        report = build_report(
            ts=candle.ts,
            signal=signal,
            final_factor=final,
            threshold=threshold,
            contrib=contrib,
            indicators={
                "rsi": indicators_row.get("rsi"),
                "macd_hist": indicators_row.get("macd_hist"),
                "cci": indicators_row.get("cci"),
                "atr": indicators_row.get("atr"),
            },
            deriv=deriv,
        )
        logger.info("Signal=%s Final=%.4f Threshold=%.4f", signal, final, threshold)
        self.maybe_notify(signal, report)

    def append_candle(self, candle: Candle):
        row = {
            "ts": candle.ts,
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
        }
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self.df = self.df.tail(2000)

    def maybe_notify(self, signal: str, report):
        now = now_ms()
        notifier_conf = self.config["notifier"]
        heartbeat_sec = self.config["polling"]["heartbeat_interval_sec"]
        send_on_change = notifier_conf.get("send_on_signal_change", True)
        if send_on_change and signal != self.last_signal and signal != "NEUTRAL":
            self.send_report(report)
            self.last_signal = signal
        if heartbeat_sec > 0 and now - self.last_heartbeat_ts >= heartbeat_sec * 1000:
            self.send_report(report)
            self.last_heartbeat_ts = now

    def send_report(self, report):  # pragma: no cover - network
        conf = self.config["notifier"]
        send_email(
            host=conf["smtp_host"],
            port=conf["smtp_port_ssl"],
            sender=conf["sender_email"],
            receivers=conf["receiver_emails"],
            subject_prefix=conf["subject_prefix"],
            auth_env=conf["sender_auth_code_env"],
            content=report.markdown,
            use_ssl=conf.get("use_ssl", True),
        )


if __name__ == "__main__":  # pragma: no cover - manual run
    runner = Runner()
    try:
        runner.start()
    except KeyboardInterrupt:
        logger.info("Runner stopped")
