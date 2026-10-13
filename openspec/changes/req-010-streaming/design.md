# Design

## Context

See proposal.md. Adapters already expose the runner seam with injected fakes; `get_adapter()` registry exists (task-005); `--probe` selection exists.

## Goals / Non-Goals

**Goals:** live pass-through + `--verbose` log files without breaking the seam, the ABC, or any fake.

**Non-Goals:** changing verdict format, log rotation, streaming `build`/`dev` output.

## Decisions

- **Extend the default runners in place** (`subprocess_runner(argv, *, stream=False, log_path=None)`): plain calls behave byte-identically (fakes untouched); streaming uses `Popen` with merged stdout+stderr, prints live, tees to file, still returns a `Transcript`.
- **Adapters opt in via constructor kwargs** (`stream`, `log_path`); `flash()` routes to the streaming runner only when the default runner is in use, else raises rather than silently dropping output (fakes capture instead).
- **Registry passes kwargs through** (`get_adapter(name, **kwargs)`); main always constructs with `stream=True` + log path iff `--verbose`, so live progress is default and raw logs are opt-in artifacts.
- **Log path** `<project>/.stm/logs/<verb>-<timestamp>.log`, dirs created up front.

## Risks / Trade-offs

- [Risk] Merged streams lose stdout/stderr distinction → Mitigation: accepted for progress display; proof payloads keep their parsed structure.
- [Risk] Non-TTY consumers get interleaved output → Mitigation: same bytes land in `--verbose` logs for post-mortem.

## Verification plan

- Streaming unit tests with a real `python -c` tool (no probe needed).
- `--verbose` main test asserting log dir + kwarg plumbing.
- Full suite green; gate scan clean.

## Open Questions

None.
