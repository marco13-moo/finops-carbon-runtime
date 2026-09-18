import unittest
from decimal import Decimal

from finops_runtime.accounting import allocate, pool_report, reconcile, reconcile_carbon
from finops_runtime.benchmark import run
from finops_runtime.model import LocationWindow, Policy, SharedPool, Usage, Workload
from finops_runtime.policy import evaluate
from finops_runtime.scheduling import choose, defer


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.usage = [
            Usage("a", "svc", "kubernetes", Decimal(1), Decimal(3)),
            Usage("b", "svc", "kubernetes", Decimal(2), Decimal(1)),
        ]
        self.pool = SharedPool("node", "kubernetes", Decimal(8), Decimal(400), Decimal(10))

    def test_shared_pool_reconciles_without_double_counting(self):
        allocations = allocate(iter(self.usage), iter([self.pool]))
        self.assertEqual(sum(a.shared_cost for a in allocations), Decimal("8.0000"))
        self.assertEqual(reconcile(allocations, [self.pool])["kubernetes"], Decimal("0.0000"))
        self.assertEqual(
            reconcile_carbon(allocations, [self.pool])["kubernetes"], Decimal("0.0000")
        )
        self.assertEqual(pool_report(allocations, [self.pool])[0]["unallocated_driver"], Decimal(6))

    def test_policy_fails_closed(self):
        allocations = allocate(self.usage, [self.pool])
        self.assertTrue(evaluate([Policy("budget", "a", max_cost=Decimal(1))], allocations))
        self.assertTrue(
            evaluate([Policy("service-budget", "service:svc", max_cost=Decimal(1))], allocations)
        )
        self.assertTrue(
            evaluate([Policy("platform-budget", "platform", max_cost=Decimal(1))], allocations)
        )

    def test_slo_guard(self):
        windows = [
            LocationWindow("fast", Decimal(1), Decimal(500), Decimal(20)),
            LocationWindow("clean", Decimal("0.5"), Decimal(100), Decimal(80)),
        ]
        self.assertEqual(choose(windows, Workload("api", Decimal(1), Decimal(30))).name, "fast")

    def test_batch_deferral_never_applies_to_interactive_workloads(self):
        windows = [
            LocationWindow("now", Decimal(1), Decimal(500), Decimal(20)),
            LocationWindow("later", Decimal("0.5"), Decimal(100), Decimal(20)),
        ]
        interactive = Workload("api", Decimal(1), Decimal(30), batch=False, deadline_window=1)
        self.assertEqual(defer(windows, interactive, windows[0]).name, "now")

    def test_multiple_pools_require_explicit_pool_and_reconcile_independently(self):
        pools = [
            SharedPool("node-a", "kubernetes", Decimal(8), Decimal(400), Decimal(10)),
            SharedPool("node-b", "kubernetes", Decimal(4), Decimal(200), Decimal(10)),
        ]
        with self.assertRaises(ValueError):
            allocate([self.usage[0]], pools)
        usage = [
            Usage("a", "svc", "kubernetes", driver=Decimal(3), pool_id="node-a"),
            Usage("b", "svc", "kubernetes", driver=Decimal(1), pool_id="node-b"),
        ]
        allocations = allocate(usage, pools)
        self.assertEqual(reconcile(allocations, pools)["kubernetes"], Decimal("0.0000"))

    def test_benchmark_proves_target(self):
        result = run()
        self.assertTrue(result["reduced_cost"])
        self.assertTrue(result["reduced_carbon"])
        self.assertTrue(result["slo_preserved"])


if __name__ == "__main__":
    unittest.main()
