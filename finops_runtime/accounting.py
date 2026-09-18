from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from decimal import Decimal

from .model import Allocation, SharedPool, Usage


def allocate(usage: Iterable[Usage], pools: Iterable[SharedPool]) -> list[Allocation]:
    usages = list(usage)
    shared_pools = list(pools)
    pools_by_resource: dict[str, list[SharedPool]] = defaultdict(list)
    for pool in shared_pools:
        pools_by_resource[pool.resource].append(pool)
    for item in usages:
        candidates = pools_by_resource[item.resource]
        if item.pool_id is None and len(candidates) > 1:
            raise ValueError(f"usage for {item.resource} must specify pool_id")
        if item.pool_id is not None and not any(p.pool_id == item.pool_id for p in candidates):
            raise ValueError(f"unknown pool_id {item.pool_id!r} for {item.resource}")
    by_pool: dict[str, Decimal] = defaultdict(Decimal)
    for item in usages:
        selected_pool = _pool_for(item, pools_by_resource[item.resource])
        if selected_pool:
            by_pool[selected_pool.pool_id] += item.driver
    allocations: list[Allocation] = []
    for item in usages:
        selected_pool = _pool_for(item, pools_by_resource[item.resource])
        shared = Decimal(0)
        carbon = Decimal(0)
        source = "direct"
        if selected_pool and by_pool[selected_pool.pool_id] > 0:
            share = item.driver / by_pool[selected_pool.pool_id]
            shared = (selected_pool.cost * share).quantize(Decimal("0.0001"))
            carbon = (selected_pool.carbon_grams * share).quantize(Decimal("0.0001"))
            source = f"shared:{selected_pool.pool_id}"
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


def _pool_for(item: Usage, candidates: list[SharedPool]) -> SharedPool | None:
    if item.pool_id is not None:
        return next((pool for pool in candidates if pool.pool_id == item.pool_id), None)
    return candidates[0] if candidates else None


def reconcile(allocations: Iterable[Allocation], pools: Iterable[SharedPool]) -> dict[str, Decimal]:
    allocated: dict[str, Decimal] = defaultdict(Decimal)
    for item in allocations:
        if item.source.startswith("shared:"):
            allocated[item.resource] += item.shared_cost
    expected: dict[str, Decimal] = defaultdict(Decimal)
    for pool in pools:
        expected[pool.resource] += pool.cost
    return {
        resource: expected.get(resource, Decimal(0)) - amount
        for resource, amount in allocated.items()
    }


def reconcile_carbon(
    allocations: Iterable[Allocation], pools: Iterable[SharedPool]
) -> dict[str, Decimal]:
    allocated: dict[str, Decimal] = defaultdict(Decimal)
    expected: dict[str, Decimal] = defaultdict(Decimal)
    for item in allocations:
        if item.source.startswith("shared:"):
            allocated[item.resource] += item.carbon_grams
    for pool in pools:
        expected[pool.resource] += pool.carbon_grams
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
        source = f"shared:{pool.pool_id}"
        allocated = sum((a.driver for a in allocations if a.source == source), Decimal(0))
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
