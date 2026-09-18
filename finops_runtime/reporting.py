from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from .accounting import tenant_totals
from .model import Allocation


def pull_request_report(
    allocations: Iterable[Allocation], changed_service: str, baseline_cost: Decimal
) -> str:
    current = sum((a.total_cost for a in allocations if a.service == changed_service), Decimal(0))
    delta = current - baseline_cost
    return f"## FinOps impact\n\n- Service: `{changed_service}`\n- Estimated cost: `${current:.4f}`\n- Baseline: `${baseline_cost:.4f}`\n- Delta: `${delta:.4f}`\n"


def unit_economics(allocations: Iterable[Allocation]) -> dict[str, Decimal]:
    totals = tenant_totals(allocations)
    return {
        tenant: (values["cost"] / values["requests"] if values["requests"] else values["cost"])
        for tenant, values in totals.items()
    }
