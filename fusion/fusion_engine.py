from typing import Dict
from core.schemas import FactorResult


def fuse_factors(factors: FactorResult, weights: Dict[str, float], threshold_k: float, volatility: float):
    final = (
        weights.get("Trend", 0) * factors.Trend
        + weights.get("Momentum", 0) * factors.Momentum
        + weights.get("Volatility", 0) * factors.Volatility
        + weights.get("LeverageFlow", 0) * factors.LeverageFlow
    )
    threshold = threshold_k * volatility
    contrib = {
        "Trend": weights.get("Trend", 0) * factors.Trend,
        "Momentum": weights.get("Momentum", 0) * factors.Momentum,
        "Volatility": weights.get("Volatility", 0) * factors.Volatility,
        "LeverageFlow": weights.get("LeverageFlow", 0) * factors.LeverageFlow,
    }
    return final, threshold, contrib
