---
id: task-022
title: "Drop the combined Build+Flash+Monitor task: it leaves the port held"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-022/
branch: ticket/task-022-split-flash-monitor
---

# Drop the combined Build+Flash+Monitor task

## Parent

`req-022` — lane inherited from parent.

## Work

The generated `Build + Flash + Monitor` task flashed and then monitored **in one
terminal** — so the monitor kept holding `/dev/ttyUSB0` after the task finished,
and the next `Flash` failed with
`Could not open /dev/ttyUSB0, the port is busy`. A task that both programs the
board and then watches it guarantees that state. Monitoring stays its own task.

## Done-when

No generated task flashes *and* monitors; the render test enforces it; `make test`
green.

## Evidence

2026-10-16 — branch `ticket/task-022-split-flash-monitor`:

- Tasks are now `Build` (`idf.py build`), `Flash` (`idf.py -p /dev/ttyUSB0 flash`),
  `Monitor` (`idf.py -p /dev/ttyUSB0 monitor --no-reset`), `Build + Flash`
  (`idf.py build && idf.py -p /dev/ttyUSB0 flash`).
- The render test asserts the label set and that `Build + Flash` contains no
  `monitor` invocation.
- The generated README says why monitoring is a separate step.
- `make test` → **355 passed**.
- Bench: the failure that motivated this is recorded in `ops-025` (a live
  `esp_idf_monitor` holding the tty; `pkill -f idf_monitor` freed it).