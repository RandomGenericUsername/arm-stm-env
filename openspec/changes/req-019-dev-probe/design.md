# Design

## Context

See proposal.md. The shim already computes the probe binding for every verb
(`build_container_argv` → `probe_docker_args`); only `dev`'s argparse lacked the
selectors, so `_run_verb` never passed them.

## Goals / Non-Goals

**Goals:** `mu dev --vid/--pid` yields a container holding the probe.

**Non-Goals:** surviving a mid-session replug (node number change).

## Decisions

- **D1 — Share the selectors.** Split `_add_probe_flags` into
  `_add_probe_selectors` (the four selector flags) + `_add_probe_flags` (selectors
  + `--verbose`). `dev` gets the selectors only (`--verbose` is flash/debug-only).
- **D2 — Reuse existing resolution.** No shim change: `build_container_argv`
  already emits `--device <node>:<node>` from the binding; passing the selectors
  through `ShimRequest` is enough.
- **D3 — `--mode local` unaffected.** `dev` local spawns the host shell; selectors
  are inert there (host has direct probe access).

## Risks / Trade-offs

- [Risk] node changes after the container starts → Mitigation: out of scope;
  follow-up (mount `/dev/bus/usb` or recreate). Documented.

## Verification plan

- Unit: `main(["dev", "--device", …])` dry-run shows `--device <node>:<node>` and
  `/bin/bash`.
- Live: `mu dev --vid 0483 --pid 3754 --dry-run` resolves `/dev/bus/usb/003/045`.
- `make test` green; `openspec validate req-019-dev-probe` green.

## Open Questions

- A detached/managed dev-container lifecycle (so VS Code attach doesn't depend on
  a foreground `mu dev`)?
