import pandas as pd
import pandas_ta as ta


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = ta.rsi(df["close"], length=14)
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df["macd_hist"] = macd["MACDh_12_26_9"]
    boll = ta.bbands(df["close"], length=20, std=2)
    df["boll_upper"] = boll["BBU_20_2.0"]
    df["boll_middle"] = boll["BBM_20_2.0"]
    df["boll_lower"] = boll["BBL_20_2.0"]
    df["ema20"] = ta.ema(df["close"], length=20)
    df["ema20_slope"] = df["ema20"].diff()
    df["cci"] = ta.cci(df["high"], df["low"], df["close"], length=20)
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
    return df
