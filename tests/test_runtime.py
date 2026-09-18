import unittest
from decimal import Decimal

from finops_runtime.accounting import allocate, pool_report, reconcile
from finops_runtime.benchmark import run
from finops_runtime.model import LocationWindow, Policy, SharedPool, Usage, Workload
from finops_runtime.policy import evaluate
from finops_runtime.scheduling import choose


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.usage = [
            Usage("a", "svc", "kubernetes", Decimal(1), Decimal(3)),
            Usage("b", "svc", "kubernetes", Decimal(2), Decimal(1)),
        ]
        self.pool = SharedPool("node", "kubernetes", Decimal(8), Decimal(400), Decimal(10))

    def test_shared_pool_reconciles_without_double_counting(self):
        allocations = allocate(self.usage, [self.pool])
        self.assertEqual(sum(a.shared_cost for a in allocations), Decimal("8.0000"))
        self.assertEqual(reconcile(allocations, [self.pool])["kubernetes"], Decimal("0.0000"))
        self.assertEqual(pool_report(allocations, [self.pool])[0]["unallocated_driver"], Decimal(6))

    def test_policy_fails_closed(self):
        allocations = allocate(self.usage, [self.pool])
        self.assertTrue(evaluate([Policy("budget", "a", max_cost=Decimal(1))], allocations))

    def test_slo_guard(self):
        windows = [
            LocationWindow("fast", Decimal(1), Decimal(500), Decimal(20)),
            LocationWindow("clean", Decimal("0.5"), Decimal(100), Decimal(80)),
        ]
        self.assertEqual(choose(windows, Workload("api", Decimal(1), Decimal(30))).name, "fast")

    def test_benchmark_proves_target(self):
        result = run()
        self.assertTrue(result["reduced_cost"])
        self.assertTrue(result["reduced_carbon"])
        self.assertTrue(result["slo_preserved"])


if __name__ == "__main__":
    unittest.main()
