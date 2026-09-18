from __future__ import annotations

import argparse
from decimal import Decimal

from .accounting import allocate, pool_report, reconcile
from .benchmark import run
from .model import SharedPool, Usage


def demo() -> None:
    usage = [
        Usage("acme", "checkout", "kubernetes", Decimal("1.20"), Decimal(60), 1200),
        Usage("beta", "reports", "kubernetes", Decimal("0.80"), Decimal(40), 400),
        Usage("acme", "checkout", "database", Decimal("0.30"), Decimal(3), 1200),
    ]
    pools = [
        SharedPool("node-pool-a", "kubernetes", Decimal(10), Decimal(1000), Decimal(100)),
        SharedPool("db-a", "database", Decimal(5), Decimal(400), Decimal(10)),
    ]
    allocations = allocate(usage, pools)
    for item in allocations:
        print(
            f"{item.tenant:6} {item.service:8} {item.resource:15} cost=${item.total_cost:.4f} carbon={item.carbon_grams:.4f} source={item.source}"
        )
    print("reconciliation:", reconcile(allocations, pools))
    print("capacity:", pool_report(allocations, pools))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["demo", "benchmark"])
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    if args.command == "demo":
        demo()
    else:
        result = run(args.smoke)
        for key, value in result.items():
            print(f"{key}={value}")
        if not all(result[k] for k in ("reduced_cost", "reduced_carbon", "slo_preserved")):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
