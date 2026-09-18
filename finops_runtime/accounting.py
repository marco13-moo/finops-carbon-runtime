from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal

from .model import Allocation, SharedPool, Usage


def allocate(usage: Iterable[Usage], pools: Iterable[SharedPool]) -> list[Allocation]:
    usages = list(usage)
    by_resource: dict[str, Decimal] = defaultdict(Decimal)
    for item in usages:
        by_resource[item.resource] += item.driver
    allocations: list[Allocation] = []
    for item in usages:
        pool = next((p for p in pools if p.resource == item.resource), None)
        shared = Decimal(0)
        carbon = Decimal(0)
        source = "direct"
        if pool and by_resource[item.resource] > 0:
            share = item.driver / by_resource[item.resource]
            shared = (pool.cost * share).quantize(Decimal("0.0001"))
            carbon = (pool.carbon_grams * share).quantize(Decimal("0.0001"))
            source = f"shared:{pool.pool_id}"
        allocations.append(
            Allocation(
                item.tenant,
                item.service,
                item.resource,
                item.direct_cost,
                shared,
                carbon,
                item.driver,
                source,
                item.requests,
            )
        )
    return allocations


def reconcile(allocations: Iterable[Allocation], pools: Iterable[SharedPool]) -> dict[str, Decimal]:
    allocated: dict[str, Decimal] = defaultdict(Decimal)
    for item in allocations:
        if item.source.startswith("shared:"):
            allocated[item.resource] += item.shared_cost
    expected: dict[str, Decimal] = {p.resource: p.cost for p in pools}
    return {
        resource: expected.get(resource, Decimal(0)) - amount
        for resource, amount in allocated.items()
    }


def pool_report(
    allocations: Iterable[Allocation], pools: Iterable[SharedPool]
) -> list[dict[str, Decimal | str]]:
    """Expose allocated, idle, and unallocated capacity without assigning it."""
    rows: list[dict[str, Decimal | str]] = []
    for pool in pools:
        allocated = sum((a.driver for a in allocations if a.resource == pool.resource), Decimal(0))
        rows.append(
            {
                "pool": pool.pool_id,
                "resource": pool.resource,
                "allocated_driver": allocated,
                "idle_driver": pool.idle_capacity,
                "unallocated_driver": max(
                    pool.capacity - allocated - pool.idle_capacity, Decimal(0)
                ),
            }
        )
    return rows


def tenant_totals(allocations: Iterable[Allocation]) -> dict[str, dict[str, Decimal]]:
    totals: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"cost": Decimal(0), "carbon": Decimal(0), "requests": Decimal(0)}
    )
    for item in allocations:
        totals[item.tenant]["cost"] += item.total_cost
        totals[item.tenant]["carbon"] += item.carbon_grams
        totals[item.tenant]["requests"] += Decimal(item.requests)
    return dict(totals)
