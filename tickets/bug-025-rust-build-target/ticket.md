---
id: bug-025
title: "mu build for Rust omits --target: compiles for the host and fails to link"
kind: bug
status: triage
lane: direct
severity: S1
links:
  openspec: none
  bmad: none
worktree: .worktrees/bug-025/
branch: ticket/bug-025-rust-build-target
repro: "uv run mu create --mcu-config stm32f411re --lang rust --name x --path /tmp/opencode/rustflash && uv run mu build --project-dir /tmp/opencode/rustflash/x"
observed: "rust-lld: error: undefined symbol: Reset ... collect2: error: ld returned 1 exit status (cargo compiled for the x86_64 host, not thumbv7em-none-eabihf)"
expected: "builds target/thumbv7em-none-eabihf/debug/<pack-id>, as the verify harness does with `cargo build --target thumbv7em-none-eabihf`"
---

# mu build for Rust omits --target: compiles for the host and fails to link

## Repro

```sh
uv run mu create --mcu-config stm32f411re --lang rust --name x --path /tmp/opencode/rustflash
uv run mu build --project-dir /tmp/opencode/rustflash/x
```

## Observed

```
rust-lld: error: undefined symbol: Reset
   >>> referenced by lib.rs:1141 (src/lib.rs:1141)
   >>> ... cortex_m_rt-...cortex_m_rt...rcgu.o:(__RESET_VECTOR) ...
rust-lld: error: undefined symbol: rust_eh_personality
   >>> ... /rustlib/x86_64-unknown-linux-gnu/lib/libcore-...rlib
collect2: error: ld returned 1 exit status
error: could not compile `stm32f411re` (bin "stm32f411re") due to 1 previous error
```

The `x86_64-unknown-linux-gnu` paths show cargo targeted the **host**, not the
Cortex-M arch. (2026-10-16, F411RE; reproduced building the generated Rust tree.)

## Expected

`cargo build --target thumbv7em-none-eabihf` runs (as the harness does) and
`target/thumbv7em-none-eabihf/debug/<pack-id>` is produced. Confirmed working:
`cargo build --target thumbv7em-none-eabihf` → `Finished dev profile in 4.51s`.

## Fix notes

`cargo-cortex`'s `build_argv` is `("cargo","build")`
(`engine/adapters/toolchain/__init__.py:24-29`) and no `.cargo/config.toml` is
rendered, so `cargo build` has no target. The verify harness only passes because
it appends `--target` itself (`engine/verify/e2e.py:339-341`); the user-facing
`mu build` (which the generated README documents, `ops-021`) does not.

Preferred fix: render `.cargo/config.toml` with `[build] target = "<core arch>"`
in the `rust-cortex` template branch (`engine/templates/renderer.py`, ~line 1466),
using `pack_model.cores[0].arch`. That keeps `mu build`'s static argv and the
generated README accurate. Add a regression test asserting the rendered tree
carries `.cargo/config.toml` with the pack arch (and that `mu build`-equivalent
`cargo build` selects the target).

Related: the generated Rust `README.md` claims a PA5 LED blink, but `src/main.rs`
is a `wfi` loop (`engine/templates/renderer.py:670`) — reconcile the README text
in the same change.
