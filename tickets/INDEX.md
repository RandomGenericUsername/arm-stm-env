# Ticket index

> Counting rule: completeness checks cover item files (`tickets/<id>-<slug>/ticket.md`) only.
> `tickets/_template/` (and any `tickets/_fixtures/`) are excluded from INDEX completeness counting.
> Entry format: link — title | `status` | execution links. Epics add `done/total children done`, done-when, and one nested line per child. Bugs add severity. Spikes add timebox state.

## Active epics

- [epic-001-universal-framework](./epic-001-universal-framework/epic.md) — Universal MCU dev framework | `decomposed` | 2/2 children done | done-when: V1 matrix completes create-build-flash-run from clean machines | exec: bmad brief+spec
  - [req-001-product-brief](./req-001-product-brief/ticket.md) — Product brief for universal MCU dev framework | `done`
  - [req-002-distill-spec](./req-002-distill-spec/ticket.md) — Distill spec from finalized brief | `done`

## Requirements

- [req-002-distill-spec](./req-002-distill-spec/ticket.md) — Distill spec from finalized brief | `done` | exec: bmad spec
- [req-001-product-brief](./req-001-product-brief/ticket.md) — Product brief for universal MCU dev framework | `done` | exec: bmad brief

## Bugs

(none)

## Ops tasks

(none)

## Spikes

(none)

## Tasks

(none)

## Done (links only, newest last)

(none)
