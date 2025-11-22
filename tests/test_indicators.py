import pandas as pd
import pandas_ta as ta
from indicators.indicator_calc import compute_indicators


def test_indicator_alignment():
    data = {
        "open": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
        "high": [x + 0.5 for x in range(1, 26)],
        "low": [x - 0.5 for x in range(1, 26)],
        "close": list(range(1, 26)),
        "volume": [100] * 25,
    }
    df = pd.DataFrame(data)
    result = compute_indicators(df)

    expected_rsi = ta.rsi(df["close"], length=14).iloc[-1]
    expected_macd_hist = ta.macd(df["close"], fast=12, slow=26, signal=9)["MACDh_12_26_9"].iloc[-1]
    expected_boll = ta.bbands(df["close"], length=20, std=2)
    expected_atr = ta.atr(df["high"], df["low"], df["close"], length=14).iloc[-1]

    assert abs(result["rsi"].iloc[-1] - expected_rsi) < 1e-6
    assert abs(result["macd_hist"].iloc[-1] - expected_macd_hist) < 1e-6
    assert abs(result["boll_upper"].iloc[-1] - expected_boll["BBU_20_2.0"].iloc[-1]) < 1e-6
    assert abs(result["atr"].iloc[-1] - expected_atr) < 1e-6
