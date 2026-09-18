# ADR-005: Synthetic before/after proof

The benchmark uses deterministic workload, price, carbon, and SLO inputs. Baseline placement runs immediately in the default region; optimized placement selects a lower score window while preserving the declared latency guard. We report total cost, carbon, and SLO pass rate before and after. Results prove only this synthetic scenario; they do not generalize to a provider or customer.
