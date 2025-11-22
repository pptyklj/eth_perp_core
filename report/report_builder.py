from typing import Dict, Optional
from core.schemas import Derivatives, SignalReport
from core.time_utils import ts_to_iso


def build_report(ts: int, signal: str, final_factor: float, threshold: float, contrib: Dict[str, float], indicators: Dict[str, float], deriv: Optional[Derivatives]):
    md_lines = [
        f"## ETH-USDT-SWAP Signal",
        f"- Time: {ts_to_iso(ts)}",
        f"- Signal: **{signal}**",
        f"- FinalFactor: {final_factor:.4f}",
        f"- Threshold: {threshold:.4f}",
        "### Factor Contribution",
    ]
    for k, v in contrib.items():
        md_lines.append(f"- {k}: {v:.4f}")
    md_lines.append("### Key Indicators")
    for k, v in indicators.items():
        md_lines.append(f"- {k}: {v}")
    if deriv:
        md_lines.append("### Derivatives")
        md_lines.append(f"- OI: {deriv.open_interest}")
        md_lines.append(f"- Funding: {deriv.funding_rate}")
    markdown = "\n".join(md_lines)
    json_obj = {
        "time": ts,
        "signal": signal,
        "final_factor": final_factor,
        "threshold": threshold,
        "factors": contrib,
        "indicators": indicators,
        "derivatives": deriv.__dict__ if deriv else None,
    }
    return SignalReport(
        timestamp=ts,
        signal=signal,
        final_factor=final_factor,
        threshold=threshold,
        factors=contrib,
        indicators=indicators,
        derivatives=deriv,
        markdown=markdown,
        json=json_obj,
    )
