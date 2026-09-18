# Architecture

The MVP is a Python package with typed domain records, pure calculation engines, and a small CLI. Ingestion accepts JSON records; the allocation engine produces auditable line items; policy, placement, forecasting, and reporting consume those line items. Pure functions make reconciliation deterministic and testable. A production deployment can place these boundaries behind an API and durable event store without changing the domain model.
