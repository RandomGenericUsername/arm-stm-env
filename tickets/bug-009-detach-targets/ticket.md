---
id: bug-009
title: "resume-on-detach cfg breaks the H7 server (undefined _TARGETNAME)"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-009/
branch: ticket/bug-009-detach-targets
repro: "mu create --mcu-config stm32h755 --lang c --name h755-clean --path ~/Desktop --vscode && F5 in the attached container"
observed: "OpenOCD: GDB Server Quit Unexpectedly; probe/resume-on-detach.cfg:5: Error: can't read \"_TARGETNAME\": no such variable"
expected: "server starts; Debug M7/M4 works"
---

# resume-on-detach cfg breaks the H7 server (undefined _TARGETNAME)

## Repro

```sh
mu create --mcu-config stm32h755 --lang c --name h755-clean --path ~/Desktop --vscode
# attach to the dev container, F5 -> Debug M7
```

## Observed

```
OpenOCD: GDB Server Quit Unexpectedly.
probe/resume-on-detach.cfg:5: Error: can't read "_TARGETNAME": no such variable
```

The req-018 cfg used `$_TARGETNAME`, which F4 target configs define but the H7
DAP config does not — so sourcing the file errors and OpenOCD exits (blocking
*all* H755 debugging, not just resume).

## Expected

The server starts and M7/M4 debug works; the target resumes on detach.

## Fix notes

Generate `probe/resume-on-detach.cfg` **per device** (`_resume_on_detach`):
- pack declares `openocd.targets` (H755 M7/M4, bug-006) → set the event on each
  declared target name (`stm32h7x.cpu0/cpu1`);
- otherwise → guarded `if {[info exists _TARGETNAME]} { … }` (no-op where the
  variable is absent, instead of an error).

Live 2026-10-14: H755 `openocd … -f probe/resume-on-detach.cfg -c "init; shutdown"`
→ no error; `stm32h7x.cpu0 curstate` = `running` after detach. F411 unchanged
(guarded `_TARGETNAME`, resume verified in req-018).
