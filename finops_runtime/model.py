from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

ResourceKind = Literal["kubernetes", "database", "observability", "network"]


@dataclass(frozen=True)
class Usage:
    tenant: str
    service: str
    resource: ResourceKind
    direct_cost: Decimal = Decimal("0")
    driver: Decimal = Decimal("0")
    requests: int = 0


@dataclass(frozen=True)
class SharedPool:
    pool_id: str
    resource: ResourceKind
    cost: Decimal
    carbon_grams: Decimal
    capacity: Decimal
    idle_capacity: Decimal = Decimal("0")


@dataclass(frozen=True)
class Allocation:
    tenant: str
    service: str
    resource: ResourceKind
    direct_cost: Decimal
    shared_cost: Decimal
    carbon_grams: Decimal
    driver: Decimal
    source: str
    requests: int = 0

    @property
    def total_cost(self) -> Decimal:
        return self.direct_cost + self.shared_cost


@dataclass(frozen=True)
class Policy:
    name: str
    scope: str
    max_cost: Decimal | None = None
    max_carbon_grams: Decimal | None = None


@dataclass(frozen=True)
class LocationWindow:
    name: str
    price_per_unit: Decimal
    carbon_intensity: Decimal
    latency_ms: Decimal


@dataclass(frozen=True)
class Workload:
    name: str
    units: Decimal
    max_latency_ms: Decimal
    weight_price: Decimal = Decimal("0.5")
    weight_carbon: Decimal = Decimal("0.5")
    batch: bool = False
    deadline_window: int = 0
