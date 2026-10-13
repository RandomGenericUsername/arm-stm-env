# Spec Delta

## Purpose

Tool output is observable while it runs: live progress by default, complete logs on request — never silence until verdict.

## ADDED Requirements

### Requirement: Live streaming by default

During `flash`/`debug`, tool stdout/stderr SHALL pass through to the terminal as produced, closing with the verdict line.

Evidence: user requirement 2026-10-13. Verify: faked slow tool output appears incrementally (timed capture test).

#### Scenario: Stuck probe visible

- **WHEN** a probe stalls mid-flash
- **THEN** the user sees the last tool line immediately, not after timeout

### Requirement: Verbose preserves full logs

With `--verbose`, the complete raw log SHALL also be written to `<project>/.stm/logs/<verb>-<timestamp>.log`.

Evidence: debugging need (post-mortem without re-running). Verify: log file exists with full transcript after run.

#### Scenario: Post-mortem without re-flash

- **WHEN** a run finishes with `--verbose`
- **THEN** the log file contains the entire tool output byte-for-byte
