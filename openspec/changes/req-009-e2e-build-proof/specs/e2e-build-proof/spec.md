# Spec Delta

## Purpose

The e2e harness proves rendered projects compile under pinned toolchains and fit their pack maps, with per-cell evidence — the last software-only proof before hardware.

## ADDED Requirements

### Requirement: All cells compile in images

All 9 cells SHALL render and complete their image build/check with exit 0.

Evidence: V1 success criteria (minus flash-run). Verify: harness exit 0 + per-cell log lines.

#### Scenario: Cell failure blocks

- **WHEN** any cell fails to compile
- **THEN** the harness exits non-zero naming the cell and keeps its full log

### Requirement: Sizes fit pack maps

Each C/C++ ELF SHALL fit its pack flash/RAM (`arm-none-eabi-size` vs map); each Rust `memory.x` SHALL match the pack origins/lengths byte-for-byte.

Evidence: pack memory maps (req-004). Verify: size assertions in harness output.

#### Scenario: Overflow fails the cell

- **WHEN** an ELF exceeds its region
- **THEN** the cell fails with used-vs-available figures

### Requirement: Warnings recorded, not failed on

The harness SHALL record warnings per cell and pass regardless (initial policy); fail-on-warning is a separate later decision.

Evidence: user-agreed policy (2026-10-09 session). Verify: evidence log contains a warnings section per cell.

#### Scenario: Warning baseline exists

- **WHEN** the harness completes
- **THEN** warnings per cell are queryable for the future policy decision
