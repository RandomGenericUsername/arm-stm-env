---
id: ops-025
title: "Document that a running monitor owns the serial port (flash then fails)"
kind: ops-task
status: done
size: XS
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-025/
branch: ticket/ops-025-monitor-port-note
---

# Document that a running monitor owns the serial port

## Work

On the bench, `Flash` failed with
`Could not open /dev/ttyUSB0, the port is busy or doesn't exist`
while a `Monitor` was still running. Nothing is wrong with mu — a serial monitor
holds the port exclusively, and the OS refuses the second opener. Say so in the
generated project README so the next person does not chase a hardware ghost.

## Done-when

The generated ESP32 README states the rule; the render test covers it; `make test`
green.

## Evidence

2026-10-16: `docker exec mu-dev-esp32cam ps aux` showed the live
`idf.py -p /dev/ttyUSB0 monitor --no-reset` + `esp_idf_monitor` processes holding
the tty. After `pkill -f idf_monitor`, an exclusive open succeeded. The README now
says to stop the monitor (`Ctrl+]`) before flashing.
