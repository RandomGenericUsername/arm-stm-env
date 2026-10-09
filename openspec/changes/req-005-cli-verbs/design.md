# Design

## Context

See proposal.md. Spine AD-5/AD-6/AD-8/AD-9/AD-10; req-003 model/structs; req-004 packs. Python argparse (stdlib, no new deps); container exec via `docker` CLI subprocess (OCI runtime choice deferred to image story — subprocess boundary keeps runtime swappable).

## Goals / Non-Goals

**Goals:** working `stm` entry with 5 thin verbs against stub adapter ports + fixtures; shim with image lookup, mounts, probe mapping; verdict rendering.

**Non-Goals:** real adapters, image builds, template contents, Windows support.

## Decisions

- **argparse + console script** (`stm = engine.cli.main:main`). Over Click/Typer: stdlib, zero new deps, verbs are thin enough to need no framework.
- **Adapter ports as ABCs** in `engine/adapters/__init__.py` (ProbeAdapter: flash/debug with multi-piece results; registry for image lookup lives in core per AD-8 fix). Stubs in tests implement the ports.
- **Shim = same package, mode flag.** `--mode auto` (default: container if image present/pullable, else error naming the missing image — never silent host fallback), `--mode local` for inside-container runs. Dry-run prints the exact `docker run` argv for review.
- **One-source enforcement at CLI layer**: `--mcu-config` XOR individual flags rejected with usage error when mixed (AD-5).

## Risks / Trade-offs

- [Risk] Docker absent on target machine → Mitigation: verbs fail fast with install hint; offline story belongs to image story, not here.
- [Risk] Stub ports drift from real adapters later → Mitigation: port ABCs are the contract; req-006 implements against them with conformance tests.

## Verification plan

- `pytest` CLI suite: no-hardware-knowledge grep empty, lookup/dry-run identical both modes, XOR rejection, 3-piece verdict rendering.
- `stm --help` + each verb `--help` render; `stm build --dry-run` prints container argv without Docker present.

## Open Questions

None.
