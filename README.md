# FinOps Carbon Runtime

An open-source, deterministic MVP for allocating platform cost and carbon, enforcing budgets, and making carbon-aware placement decisions.

## Quick start

```bash
python -m finops_runtime demo
python -m unittest discover -s tests -v
```

The implementation uses only the Python standard library (Python 3.11+). See [docs/architecture.md](docs/architecture.md) for the design and `examples/` for deterministic input data.

## Scope

This project demonstrates a defensible accounting model and operational workflow. It is not a cloud billing connector or a claim of production savings. The benchmark is synthetic and its assumptions are documented in [ADR-005](docs/adr/005-benchmark-methodology.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
