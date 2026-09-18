from __future__ import annotations

from decimal import Decimal

from .model import Allocation, Policy


def _totals(allocations: list[Allocation]) -> dict[str, tuple[Decimal, Decimal]]:
    totals: dict[str, tuple[Decimal, Decimal]] = {}
    for item in allocations:
        keys = {"platform", f"tenant:{item.tenant}", f"service:{item.service}"}
        for key in keys:
            cost, carbon = totals.get(key, (Decimal(0), Decimal(0)))
            totals[key] = cost + item.total_cost, carbon + item.carbon_grams
    return totals


def evaluate(policies: list[Policy], allocations: list[Allocation]) -> list[str]:
    violations: list[str] = []
    totals = _totals(allocations)
    for policy in policies:
        scope = policy.scope
        key = scope if scope in {"platform"} or ":" in scope else f"tenant:{scope}"
        cost, carbon = totals.get(key, (Decimal(0), Decimal(0)))
        if policy.max_cost is not None and cost > policy.max_cost:
            violations.append(f"{policy.name}: {policy.scope} cost {cost} > {policy.max_cost}")
        if policy.max_carbon_grams is not None and carbon > policy.max_carbon_grams:
            violations.append(
                f"{policy.name}: {policy.scope} carbon {carbon} > {policy.max_carbon_grams}"
            )
    return violations
