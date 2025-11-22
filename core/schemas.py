from __future__ import annotations
import dataclasses
from typing import List, Optional, Dict


@dataclasses.dataclass
class Candle:
    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    confirm: int
    source: str = "OKX"
    is_filled: bool = False


@dataclasses.dataclass
class Derivatives:
    ts: int
    instId: str
    open_interest: float
    funding_rate: float
    source: str = "OKX"


@dataclasses.dataclass
class FactorResult:
    Trend: float
    Momentum: float
    Volatility: float
    LeverageFlow: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class FactorContrib:
    weights: Dict[str, float]
    factors: Dict[str, float]
    final_factor: float
    threshold: float


@dataclasses.dataclass
class SignalReport:
    timestamp: int
    signal: str
    final_factor: float
    threshold: float
    factors: Dict[str, float]
    indicators: Dict[str, float]
    derivatives: Optional[Derivatives]
    markdown: str
    json: Dict
