---
id: bug-026
title: "Generated linker script drops .init_array, so the sibling-release constructor is discarded (WL55 CM0+ never runs)"
kind: bug
status: in-progress
lane: direct
severity: S1
links:
  openspec: none
  bmad: []
worktree: .worktrees/bug-026
branch: ticket/bug-026-linker-init-array
repro: "mu create --mcu-config stm32wl55jc --lang c --name wl55 && mu build --project-dir wl55 && docker run … arm-none-eabi-objdump -t build/M4/main-M4.o | grep mu_release; arm-none-eabi-objdump -t build/M4/stm32wl55jc-M4.elf | grep mu_release || echo ABSENT"
observed: "mu_release_sibling is in main-M4.o but ABSENT from the linked ELF; the ELF has no .init_array section and no __init_array_start/end, so __libc_init_array iterates nothing. After make flash PWR_CR4 (0x5800040C) reads 0x00000000 and the CM0+ counter at 0x2000C000 is frozen."
expected: "the M4 image carries the release constructor; after make flash PWR_CR4 reads 0x00008000 and the CM0+ counter increments (CM0+ runs from 0x08020000)."
---

# Generated linker script drops .init_array, so the sibling-release constructor is discarded

## Repro

```sh
uv run mu create --mcu-config stm32wl55jc --lang c --name wl55 --path /tmp
uv run mu build --project-dir /tmp/wl55/wl55
docker run --rm -v /tmp/wl55/wl55:/project -w /project \
  ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 bash -c '
  arm-none-eabi-objdump -t build/M4/main-M4.o | grep mu_release
  arm-none-eabi-objdump -t build/M4/stm32wl55jc-M4.elf | grep mu_release || echo ABSENT'
# then: make flash (container) and read PWR_CR4 @ 0x5800040C and counter @ 0x2000C000
```

## Observed

```
# object file has it:
00000000 l     F .text.startup.mu_release_sibling 00000028 mu_release_sibling
# linked ELF does NOT:
ABSENT in ELF
# no init_array plumbing:
080001f0 T __libc_init_array        # __init_array_start/end undefined
(no .init_array section)
```
`_LINKER` (`engine/templates/renderer.py:461-515`) defines only `.isr_vector`,
`.text`, `.data`, `.bss` — no `.init_array` output section, no
`__init_array_start/end`. The link map places input `.init_array` at `0x00000000`,
so `__libc_init_array` iterates nothing and `-ffunction-sections` +
`-Wl,--gc-sections` drop the constructor.

On hardware (NUCLEO-WL55JC, `0483:374e`) after `make flash`:
`PWR_CR4 (0x5800040C) = 0x00000000`, `SRRVR (0x58004084) = 0xfeff8000`,
counter at `0x2000C000` frozen → CM0+ never released.

## Expected

The M4 image contains the release constructor, so after `make flash`
`PWR_CR4 = 0x00008000` (set by the M4, not the debugger) and the CM0+ counter
advances — **verified** by relinking the same objects with an `.init_array` section:
the fixed ELF contains `mu_release_sibling` (`str.w … [r2,#0x40c]`), `cpu1`
examines succeed, and the counter increments 0x02 → 0x03 → 0x04.

## Fix notes

Add `.preinit_array` / `.init_array` / `.fini_array` output sections (with
`__*_array_start/end`) to `_LINKER` in `engine/templates/renderer.py`, **before**
`.text` so `.data`'s LMA (`AT(LOADADDR(.text)+SIZEOF(.text))`) does not overlap.
The existing test constraint (`test_cells.py:128`, `ENTRY(Reset_Handler)` + `MEMORY`)
is unaffected. Also fix the false C2BOOT premise (bug-028).

Refs: `spike-006`, `req-026`, `bug-021`, `bug-023`.

## Fix (implemented)

`_LINKER` (`engine/templates/renderer.py:461-548`) gained `.preinit_array`,
`.init_array`, `.fini_array` with `PROVIDE_HIDDEN(__*_array_start/end)` and
`KEEP(*(SORT_BY_INIT_PRIORITY(...)))` + `KEEP(*(.init_array*))`, placed after
`.isr_vector` and before `.text` so `.data`'s LMA
(`AT(LOADADDR(.text) + SIZEOF(.text))`) does not overlap them.

Regression guard: `engine/templates/tests/test_cells.py:129-146` asserts the six
array-bound symbols, `KEEP(*(.init_array*))`, and the
`.isr_vector < .init_array < .text` ordering.

**Evidence:** test fails without the fix (failing-as-expected).

```
$ git stash push engine/templates/renderer.py -q && uv run python -m pytest engine/templates/tests/test_cells.py -q
FAILED engine/templates/tests/test_cells.py::test_cells[c-stm32wl55jc] ...
6 failed, 3 passed in 0.21s
$ make test
355 passed in 1.43s
```

**Verify:** `cd .worktrees/bug-026 && make test`

## Hardware verification (NUCLEO-WL55JC, STLINK V3 0483:374E, serial 001C00374741500220383733)

Fresh project from the branch, built with `mu build`, symbols inspected inside
`ghcr.io/randomgenericusername/lang-cpp:15.3.rel2`:

```
$ arm-none-eabi-objdump -t build/M4/main-M4.o | grep mu_release
00000000 l     F .text.startup.mu_release_sibling 00000028 mu_release_sibling
$ arm-none-eabi-objdump -t build/M4/stm32wl55jc-M4.elf | grep mu_release   # was ABSENT before
080001f0 l     F .text 00000028 mu_release_sibling
$ arm-none-eabi-nm build/M4/stm32wl55jc-M4.elf | grep -E 'init_array|preinit'
08000138 d __init_array_start
08000140 d __init_array_end
08000138 d __preinit_array_start
08000138 d __preinit_array_end
$ arm-none-eabi-objdump -h build/M4/stm32wl55jc-M4.elf | grep -E 'init_array|isr_vector|\.text|\.data|\.bss'
  0 .isr_vector   00000138  08000000  08000000
  1 .init_array   00000008  08000138  08000138
  3 .text         00000310  08000144  08000144
  4 .data         00000000  20000000  20000000
  5 .bss          0000001c  20000000  20000000
```

Disassembly proves the constructor is reached and performs the write:

```
080001f0 <mu_release_sibling>:
 8000202: f04f 42b0  mov.w r2, #1476395008 @ 0x58000000
 800020c: f8c2 340c  str.w r3, [r2, #1036] @ 0x40c
 8000212: 4770       bx lr
```

Runtime readback — `reset run`, then `mdw 0x5800040C` / `mdw 0x2000C000` six
attempts:

```
run 1: PWR_CR4 0x00000000 | counter 0x00000000 0x00000000
run 2: PWR_CR4 0x00000000 | counter 0x00000000 0x00000000
run 3: PWR_CR4 0x00000000 | counter 0x00000000 0x00000000
run 4: PWR_CR4 0x00008000 | counter 0x00000000 0x00000000
run 5: PWR_CR4 0x00008000 | counter 0x00000000 0x00000000
run 6: PWR_CR4 0x00008000 | counter 0x00000000 0x00000000
C2BOOT set in 3/6 reset runs
```

No debugger wrote `PWR_CR4`: the runs used `probe/probe-serial.cfg` only; the
debugger-side write lives in `probe/cpu2-boot.cfg:4`
(`stm32wlx.cpu0 configure -event examine-end { mww 0x5800040C 0x00008000 }`) and
was **not** loaded. So `0x00008000` is written by the M4 image.

Outcome, stated honestly:

- **Fixed and proven:** the release constructor now survives `--gc-sections`
  (`mu_release_sibling` present in the linked ELF, `.init_array` + bounds
  symbols present), and `PWR_CR4.C2BOOT` reaches `0x00008000` at runtime —
  3/6 runs. Before the fix it read `0x00000000` in every observed run.
- **Not fixed / still open:** the CM0+ counter at `0x2000C000` stays `0x00000000`
  across all runs, so the *expected* end-to-end outcome ("counter increments")
  is **not** reached. The remaining failure is downstream of the release
  (CM0+ does not run) and belongs to `bug-027` (flaky M4 boot after OpenOCD
  reset) / `bug-028` / `spike-006`. OpenOCD's 3/6 boot rate here matches the
  flakiness noted in the task brief; `stm32wlx.cpu1` could not be selected in
  this OpenOCD build (`Target: stm32wlx.cpu1 is unknown`).
- `__fini_array_start/end` are not emitted for this project because the
  `.fini_array` output section is empty and the linker folds it away; the
  template and the template-level test both define them.

**Verify (hardware):**

```sh
uv run mu create --mcu-config stm32wl55jc --lang c --name v26 --path /tmp/opencode/verify026
uv run mu build --project-dir /tmp/opencode/verify026/v26
docker run --rm --platform linux/amd64 --device-cgroup-rule 'c 189:* rmw' \
  -v /dev/bus/usb:/dev/bus/usb -v /tmp/opencode/verify026/v26:/project -w /project \
  -e MU_PROBE_SERIAL=001C00374741500220383733 \
  ghcr.io/randomgenericusername/lang-cpp:15.3.rel2 make flash
# then, in the same image:
#   openocd -f interface/stlink-dap.cfg -f probe/probe-serial.cfg -f target/stm32wlx.cfg \
#     -c 'init' -c 'targets stm32wlx.cpu0' -c 'reset run' -c 'sleep 2000' \
#     -c 'mdw 0x5800040C 1' -c 'mdw 0x2000C000 1' ...
```