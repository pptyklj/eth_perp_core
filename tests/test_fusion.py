from core.schemas import FactorResult
from fusion.fusion_engine import fuse_factors


def test_fuse_factors_linear_combination():
    factors = FactorResult(Trend=0.5, Momentum=-0.2, Volatility=0.3, LeverageFlow=0.1)
    weights = {"Trend": 0.25, "Momentum": 0.2, "Volatility": 0.1, "LeverageFlow": 0.45}
    final, threshold, contrib = fuse_factors(factors, weights, threshold_k=0.7, volatility=factors.Volatility)
    expected_final = 0.25 * 0.5 + 0.2 * -0.2 + 0.1 * 0.3 + 0.45 * 0.1
    assert abs(final - expected_final) < 1e-9
    assert threshold == 0.7 * factors.Volatility
    assert contrib["Trend"] == weights["Trend"] * factors.Trend
