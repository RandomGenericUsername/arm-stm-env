# Proposal

## Why

`mu flash` resolves the probe to its `/dev/bus/usb/…` node and passes it to the
container automatically (`engine/cli/shim.py`). `mu dev` does **not** accept
probe selectors, so a dev container cannot be given the probe — the user (or
agent) must hand-roll `docker run --device …` and re-resolve the node on every
start / replug. That's the friction behind the "stale node → GDB Server Quit
Unexpectedly" and the "lost container" episodes (2026-10-14).

## What Changes

- `mu dev` gains the probe selector flags (`--device`/`--vid`/`--pid`/`--serial`)
  — the same resolution `flash`/`debug` use. The dev container then receives the
  probe's USB node as `--device`, so `mu dev --vid … --pid …` is self-contained.

## Capabilities

### Modified Capabilities

- `cli-verbs`: `dev` accepts probe selectors.

## Impact

- Code: `engine/cli/main.py` (`_add_probe_selectors` shared; `dev` wired), tests.
- **Out of scope:** re-enumeration *during* a session (node changes mid-run) —
  that needs a different device-binding strategy (mount the bus / re-create);
  recorded as a follow-up.
