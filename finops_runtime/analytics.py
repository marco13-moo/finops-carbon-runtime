from __future__ import annotations

from decimal import Decimal
from statistics import mean


def forecast(values: list[Decimal], periods: int = 1) -> list[Decimal]:
    if not values:
        raise ValueError("at least one value is required")
    if len(values) == 1:
        slope = Decimal("0")
    else:
        slope = (values[-1] - values[0]) / Decimal(len(values) - 1)
    return [values[-1] + slope * Decimal(i) for i in range(1, periods + 1)]


def anomalies(values: list[Decimal], threshold: Decimal = Decimal("2")) -> list[int]:
    if len(values) < 2:
        return []
    baseline = Decimal(str(mean([float(v) for v in values[:-1]])))
    if baseline == 0:
        return [len(values) - 1] if values[-1] else []
    return [len(values) - 1] if values[-1] / baseline >= threshold else []


def recommendations(allocations) -> list[str]:
    by_tenant = {}
    for item in allocations:
        by_tenant[item.tenant] = by_tenant.get(item.tenant, Decimal("0")) + item.driver
    return [f"rightsizing candidate: {tenant} has {driver} shared-driver units"
            for tenant, driver in by_tenant.items() if driver == 0]
