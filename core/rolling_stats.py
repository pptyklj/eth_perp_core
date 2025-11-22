import numpy as np
import pandas as pd


class RollingPercentile:
    def __init__(self, window: int, percentile: float = 95):
        self.window = window
        self.percentile = percentile
        self.values = []

    def update(self, value: float):
        if value is None or np.isnan(value):
            return None
        self.values.append(value)
        if len(self.values) > self.window:
            self.values.pop(0)
        return np.percentile(self.values, self.percentile)

    def current(self) -> float:
        if not self.values:
            return np.nan
        return float(np.percentile(self.values, self.percentile))


class RollingNormalizer:
    def __init__(self, window: int):
        self.window = window
        self.values = []

    def update(self, value: float):
        if value is None or np.isnan(value):
            return None
        self.values.append(value)
        if len(self.values) > self.window:
            self.values.pop(0)
        return self.normalize(value)

    def normalize(self, value: float) -> float:
        if not self.values:
            return 0.0
        series = pd.Series(self.values)
        min_v, max_v = series.min(), series.max()
        if max_v - min_v == 0:
            return 0.0
        return float((value - min_v) / (max_v - min_v))
