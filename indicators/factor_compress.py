import numpy as np
import pandas as pd
from core.rolling_stats import RollingPercentile, RollingNormalizer
from core.schemas import FactorResult


class FactorCompressor:
    def __init__(self, rolling_window_days: int = 14, bars_per_day: int = 1440):
        window = rolling_window_days * bars_per_day
        self.macd_p95 = RollingPercentile(window=window, percentile=95)
        self.oi_p95 = RollingPercentile(window=window, percentile=95)
        self.vol_norm = RollingNormalizer(window=window)

    def compress_trend(self, df: pd.DataFrame) -> float:
        macd_hist = df["macd_hist"].iloc[-1]
        slope = df["ema20_slope"].iloc[-1]
        direction = 0
        if macd_hist > 0 and slope > 0:
            direction = 1
        elif macd_hist < 0 and slope < 0:
            direction = -1
        strength_scale = self.macd_p95.update(abs(macd_hist)) or self.macd_p95.current()
        if np.isnan(strength_scale) or strength_scale == 0:
            strength_scale = 1
        strength = np.clip(abs(macd_hist) / strength_scale, 0, 1)
        return direction * strength

    def compress_momentum(self, df: pd.DataFrame) -> float:
        rsi = df["rsi"].iloc[-1]
        cci = df["cci"].iloc[-1]
        direction = 0
        if rsi < 30 or cci < -100:
            direction = 1
        elif rsi > 70 or cci > 100:
            direction = -1
        strength = np.clip(abs(rsi - 50) / 50, 0, 1)
        return direction * strength

    def compress_volatility(self, df: pd.DataFrame) -> float:
        upper = df["boll_upper"].iloc[-1]
        lower = df["boll_lower"].iloc[-1]
        middle = df["boll_middle"].iloc[-1]
        close = df["close"].iloc[-1]
        atr = df["atr"].iloc[-1]
        boll_width = (upper - lower) / middle if middle else 0
        atr_norm = atr / close if close else 0
        vol_raw = 0.5 * boll_width + 0.5 * atr_norm
        vol_norm = self.vol_norm.update(vol_raw) or self.vol_norm.normalize(vol_raw)
        return np.clip(vol_norm, 0, 1)

    def compress_leverage_flow(self, current, previous) -> float:
        oi_change = 0.0
        funding_change = 0.0
        if current and previous and previous.open_interest != 0:
            oi_change = (current.open_interest - previous.open_interest) / previous.open_interest
            funding_change = current.funding_rate - previous.funding_rate
        direction = 0
        if oi_change > 0 and funding_change > 0:
            direction = 1
        elif oi_change > 0 and funding_change < 0:
            direction = -1
        else:
            direction = 0
        scale = self.oi_p95.update(abs(oi_change)) or self.oi_p95.current()
        if np.isnan(scale) or scale == 0:
            scale = 1
        strength = np.clip(abs(oi_change) / scale, 0, 1)
        return direction * strength

    def compute_all(self, df: pd.DataFrame, current_deriv=None, prev_deriv=None) -> FactorResult:
        return FactorResult(
            Trend=self.compress_trend(df),
            Momentum=self.compress_momentum(df),
            Volatility=self.compress_volatility(df),
            LeverageFlow=self.compress_leverage_flow(current_deriv, prev_deriv) if current_deriv else 0.0,
        )
