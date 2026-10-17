---
id: bug-026
title: "Generated linker script drops .init_array, so the sibling-release constructor is discarded (WL55 CM0+ never runs)"
kind: bug
status: triage
lane: direct
severity: S1
links:
  openspec: none
  bmad: []
worktree: none
branch: none
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