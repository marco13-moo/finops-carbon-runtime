# Architecture

The MVP is a Python package with typed domain records, pure calculation engines, and a small CLI. Ingestion accepts JSON records; the allocation engine produces auditable line items; policy, placement, forecasting, and reporting consume those line items. Pure functions make reconciliation deterministic and testable. A production deployment can place these boundaries behind an API and durable event store without changing the domain model.

Accounting is direct usage plus one shared allocation per pool:
`allocated_cost(t) = pool_cost * driver(t) / Σ driver`. Capacity is partitioned into allocated, explicitly idle, and unallocated portions. The same line items feed cost per request/customer, forecasts, anomaly checks, policy gates, and PR reports.

ADR implementation map:

| ADR | Code path | Proof |
| --- | --- | --- |
| 001 | `model.py`, pure standard-library modules | `compileall`, mypy |
| 002 | `accounting.py` | pool reconciliation and idle-capacity tests |
| 003 | `scheduling.py` | latency guard and non-deferrable interactive test |
| 004 | `policy.py` | tenant, service, and platform budget tests |
| 005 | `benchmark.py` | deterministic benchmark smoke test |

Policy scopes accept a bare tenant name for compatibility, or explicit `tenant:<id>`, `service:<name>`, and `platform` keys.
