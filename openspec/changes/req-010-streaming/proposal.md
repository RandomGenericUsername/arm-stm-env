# Proposal

## Why

Flash runs blind today: output is captured and only the verdict line surfaces. Watching the tool move is the difference between diagnosing a stuck probe in seconds versus staring at silence — requested explicitly for the flash workflow.

Evidence: user requirement (2026-10-13); proof wiring covers result data, never live output.

## What Changes

- Runner seam gains streaming: tool stdout/stderr pass through to the terminal live during `flash`/`debug`, while the transcript is still captured for proof.
- `--verbose` flag (flash/debug): preserves the complete raw log to `<project>/.stm/logs/<verb>-<timestamp>.log` in addition to live output.
- Default output: live progress lines + closing verdict (readable, no firehose).

## Capabilities

### New Capabilities

- `log-streaming`: live tool output + `--verbose` log files.

### Modified Capabilities

(none)

## Impact

- `engine/adapters/*` runner seam + `engine/cli/main.py` (`--verbose` flag, log path). No adapter logic changes.
- Out of scope: changing verdict format, log rotation policy.
