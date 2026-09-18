from __future__ import annotations

from decimal import Decimal

from .model import LocationWindow, Workload


def _score(
    window: LocationWindow, workload: Workload, max_price: Decimal, max_carbon: Decimal
) -> Decimal:
    price = window.price_per_unit / max_price if max_price else Decimal(0)
    carbon = window.carbon_intensity / max_carbon if max_carbon else Decimal(0)
    return workload.weight_price * price + workload.weight_carbon * carbon


def choose(window_list: list[LocationWindow], workload: Workload) -> LocationWindow:
    if not window_list:
        raise ValueError("at least one placement window is required")
    if workload.units <= 0:
        raise ValueError("workload units must be positive")
    eligible = [w for w in window_list if w.latency_ms <= workload.max_latency_ms]
    if not eligible:
        raise ValueError("no placement satisfies the SLO latency guard")
    max_price = max(w.price_per_unit for w in window_list)
    max_carbon = max(w.carbon_intensity for w in window_list)
    return min(eligible, key=lambda w: _score(w, workload, max_price, max_carbon))


def defer(
    window_list: list[LocationWindow], workload: Workload, current: LocationWindow
) -> LocationWindow:
    if not workload.batch or workload.deadline_window <= 0:
        return current
    selected = choose(window_list, workload)
    return (
        selected
        if _score(
            selected,
            workload,
            max(w.price_per_unit for w in window_list),
            max(w.carbon_intensity for w in window_list),
        )
        < _score(
            current,
            workload,
            max(w.price_per_unit for w in window_list),
            max(w.carbon_intensity for w in window_list),
        )
        else current
    )
