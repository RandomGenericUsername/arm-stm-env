# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.

## Epics

- [epic-001-dual-mode-cli/ticket.md](epic-001-dual-mode-cli/ticket.md) — Dual-mode CLI spine | `decomposed` | 0/1 children done | done-when: Containerized interactive dev env and host-transparent compile/build/flash both work with zero host deps | exec: none
  - [req-011-container-dev/ticket.md](req-011-container-dev/ticket.md) — Containerized interactive dev env | `triaged`

## Requirements

- [req-011-container-dev/ticket.md](req-011-container-dev/ticket.md) — Containerized interactive dev env | `triaged` | exec: none

## Bugs

- [bug-003-flash-second-run/ticket.md](bug-003-flash-second-run/ticket.md) — Flash fails on second run without power cycle | `repro-confirmed` | S2 | exec: none

## Ops tasks

- [ops-005-bump-runner/ticket.md](ops-005-bump-runner/ticket.md) — Bump CI runner image | `triaged` | exec: none

## Spikes

- [spike-002-probe-backend/ticket.md](spike-002-probe-backend/ticket.md) — Probe backend choice (OpenOCD vs pyOCD) | `boxed` | boxed 4h | exec: none

## Tasks

- [task-004-dockerfile-skeleton/ticket.md](task-004-dockerfile-skeleton/ticket.md) — Dockerfile skeleton for dev image | `triaged` | parent: req-011 | exec: none
