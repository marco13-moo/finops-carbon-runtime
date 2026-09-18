from __future__ import annotations

from decimal import Decimal

from .model import Allocation, Policy


def evaluate(policies: list[Policy], allocations: list[Allocation]) -> list[str]:
    violations: list[str] = []
    totals: dict[str, tuple[Decimal, Decimal]] = {}
    for item in allocations:
        cost, carbon = totals.get(item.tenant, (Decimal(0), Decimal(0)))
        totals[item.tenant] = cost + item.total_cost, carbon + item.carbon_grams
    for policy in policies:
        cost, carbon = totals.get(policy.scope, (Decimal(0), Decimal(0)))
        if policy.max_cost is not None and cost > policy.max_cost:
            violations.append(f"{policy.name}: {policy.scope} cost {cost} > {policy.max_cost}")
        if policy.max_carbon_grams is not None and carbon > policy.max_carbon_grams:
            violations.append(
                f"{policy.name}: {policy.scope} carbon {carbon} > {policy.max_carbon_grams}"
            )
    return violations
