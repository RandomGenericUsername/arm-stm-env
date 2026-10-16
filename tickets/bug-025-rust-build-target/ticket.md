---
id: bug-025
title: "mu build for Rust omits --target: compiles for the host and fails to link"
kind: bug
status: done
lane: direct
severity: S1
links:
  openspec: none
  bmad: none
worktree: .worktrees/bug-025/
branch: ticket/bug-025-rust-build-config
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
is a `wfi` loop (`engine/templates/renderer.py:670`) — reconciled in this fix.

## Fix

- `engine/templates/renderer.py`: new `_CARGO_CONFIG` template; the `rust-cortex`
  branch writes `.cargo/config.toml` with `[build] target = "<cores[0].arch>"`.
- `engine/templates/renderer.py` (`_readme`): the LED / sibling-core bullet lines
  are now emitted only for `c`/`cpp` — the Rust README no longer claims an LED.
- Tests: `test_cells.py` asserts `.cargo/config.toml` exists with the pack arch
  (and lists it in `expected_files`); `test_renderer.py` asserts the Rust README
  has no `on-board LED` claim.

## Evidence

```
$ cat .cargo/config.toml
[build]
target = "thumbv7em-none-eabihf"

$ uv run mu build --project-dir /tmp/opencode/rustfix/fix-f411   # no --target
   Finished `dev` profile [unoptimized + debuginfo] target(s) in 7.38s

$ readelf -h target/thumbv7em-none-eabihf/debug/stm32f411re
ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), statically linked

$ make test  →  355 passed
```

Verify: `uv run mu create --mcu-config stm32f411re --lang rust --name x --path /tmp/rustfix && uv run mu build --project-dir /tmp/rustfix/x`
