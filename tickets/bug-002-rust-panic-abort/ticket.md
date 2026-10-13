---
id: bug-002
title: "Rendered Rust projects fail to compile (unwinding panics)"
kind: bug
status: done
severity: S1
parent: epic-001
lane: openspec-single
links:
  openspec: []
  bmad: []
worktree: .worktrees/bug-002/
branch: ticket/bug-002-rust-panic-abort
---

## Repro (REQUIRED)

- command: `cargo build --target thumbv7em-none-eabihf` in rendered Rust project (rust image)
- observed: `error: unwinding panics are not supported without std` (default unwind strategy on no_std target)
- expected: green build (proven fix: `panic = "abort"` in both profiles builds on stable in 21s)

## Regression check

- check: cell tests assert `panic = "abort"` in rendered `[profile.dev]` + `[profile.release]`; F411RE + H755 rust cells compile live
