# ADR-002: Direct-first weighted allocation

Direct usage is attributed first. Each shared pool is then allocated by an explicit driver: CPU-seconds for Kubernetes nodes, connection-hours for databases, event-bytes for observability, and byte-seconds for network traffic. A tenant's share is `pool_cost * tenant_driver / sum(driver)`. Unallocated or idle capacity is reported separately, never assigned to tenants, and every pool reconciles to its source total within decimal tolerance. Shared costs are allocated once only.

When more than one pool exists for a resource kind, usage must include an explicit `pool_id`; ambiguous usage is rejected rather than guessed.
