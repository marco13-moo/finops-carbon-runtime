# ADR-003: Price/carbon score with SLO guard

Placement ranks eligible regions by normalized price and carbon intensity using configurable weights. A candidate is eligible only if its latency/SLO guard passes. Batch jobs may defer to a future window when the score improves and the deadline remains satisfiable; interactive workloads are never deferred.
