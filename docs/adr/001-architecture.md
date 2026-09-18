# ADR-001: Standard-library Python package

We use Python 3.11 dataclasses and the standard library for the MVP. This keeps local execution reproducible and makes formulas inspectable. Domain logic is dependency-free; adapters can later add cloud billing and Kubernetes clients.
