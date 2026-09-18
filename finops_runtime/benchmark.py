from __future__ import annotations

from decimal import Decimal
from .model import LocationWindow, Workload
from .scheduling import choose


def run(smoke: bool = False) -> dict[str, Decimal | bool]:
    windows = [
        LocationWindow("default", Decimal("1.00"), Decimal("450"), Decimal("30")),
        LocationWindow("clean-window", Decimal("0.70"), Decimal("120"), Decimal("35")),
    ]
    workload = Workload("batch", Decimal("100"), Decimal("50"), batch=True, deadline_window=1)
    baseline = windows[0]
    optimized = choose(windows, workload)
    base_cost = workload.units * baseline.price_per_unit
    new_cost = workload.units * optimized.price_per_unit
    base_carbon = workload.units * baseline.carbon_intensity
    new_carbon = workload.units * optimized.carbon_intensity
    slo_preserved = optimized.latency_ms <= workload.max_latency_ms
    return {"baseline_cost": base_cost, "optimized_cost": new_cost,
            "baseline_carbon": base_carbon, "optimized_carbon": new_carbon,
            "slo_preserved": slo_preserved, "reduced_cost": new_cost < base_cost,
            "reduced_carbon": new_carbon < base_carbon}
