# Spec Delta

## Purpose

Ending a debug session must not leave the firmware frozen.

## ADDED Requirements

### Requirement: Generated debug config resumes the target on detach

`create --vscode` SHALL emit `probe/resume-on-detach.cfg` (OpenOCD
`gdb-detach` → `resume`) and SHALL include it in each launch config's
`configFiles`, so a session ended by detach leaves the firmware running.

Evidence: cortex-debug #894; live `curstate` probe (design D2). Verify:
`render(..., vscode=True)` writes the cfg and `configFiles` lists it.

#### Scenario: Detach leaves the target running

- **WHEN** a debug session ends with "Disconnect" (detach)
- **THEN** the target resumes (firmware keeps running), not halted

#### Scenario: Config is wired

- **WHEN** `stm32f411re` renders with `--vscode`
- **THEN** `probe/resume-on-detach.cfg` exists and `configFiles` includes it
