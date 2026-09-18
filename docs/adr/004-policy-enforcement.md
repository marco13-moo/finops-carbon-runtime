# ADR-004: Same policy engine in CI and runtime

Budgets and carbon limits are represented as typed policies and evaluated against the same report in pull-request CI and runtime admission. Violations are explicit, stable, and fail closed. A policy can be scoped to a tenant, service, or total platform.
