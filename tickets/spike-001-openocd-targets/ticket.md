---
id: spike-001
title: "Per-pack OpenOCD target verification"
kind: spike
status: reporting
parent: epic-001
timebox: "3h"
links:
  openspec: none
  bmad: []
worktree: ""
branch: ""
---

## Questions

1. What are the correct OpenOCD interface/target configs for F411RE, H755 (both cores), WL55JC against the current ST OpenOCD fork?
2. Which sibling configs are wrong and what replaces them?

## Findings

### Answered

1. F411RE (single M4): `interface/stlink.cfg` + `board/st_nucleo_f4.cfg`
   (board sources `interface/stlink.cfg`, `transport select hla_swd`,
   `target/stm32f4x.cfg`). Evidence: ST fork `openocd-cubeide-r7`,
   `tcl/board/st_nucleo_f4.cfg:1-14` (webfetch 2026-10-08) — "This is for
   all ST NUCLEO with any STM32F4 ... STM32F411RET6". Verify: `openocd -f
   interface/stlink.cfg -f board/st_nucleo_f4.cfg`.
2. H755 (M7+M4): `interface/stlink-dap.cfg` + `board/st_nucleo_h745zi.cfg`
   (board sources `interface/stlink-dap.cfg`, `transport select
   dapdirect_swd`, `set DUAL_CORE 1`, `set USE_CTI 1`, sources
   `target/stm32h7x_dual_bank.cfg`). Evidence: `tcl/board/
   st_nucleo_h745zi.cfg:1-13`, `tcl/target/stm32h7x.cfg:27-50`
   ("Warning : hla does not support multicore debugging" — HLA falls back
   to single core, so dapdirect is mandatory for dual-core). Naming note:
   no H755-specific board file in fork; H745ZI board cfg drives the shared
   family target, acceptable for H755 (same M7+M4 + dual-bank flash).
   Verify: `openocd -f interface/stlink-dap.cfg -f
   board/st_nucleo_h745zi.cfg` on HW.
3. WL55JC (M4 + M0+, exactly 2 cores — no third core): no WL board file in
   fork (404 on `tcl/board/st_nucleo_wl55jc.cfg`), so `interface/
   stlink.cfg` + `target/stm32wlx.cfg` direct, with `set DUAL_CORE 1` for
   dual-core sessions. Evidence: `tcl/target/stm32wlx.cfg:1-60` (creates
   cpu0 CM4 + cpu1 only under DUAL_CORE; "hla does not support multicore
   debugging"). Consequence: sibling's `stlink` (HLA) is fine for
   single-core CM4 flash but CANNOT do dual-core debug — needs
   `stlink-dap` + DUAL_CORE for that. Verify: `openocd -f
   interface/stlink.cfg -f target/stm32wlx.cfg -c "set DUAL_CORE 1"`.
4. Suspect verdicts (CORRECTED by orchestrator re-verification, 2026-10-08 — agent checked the wrong project for (c) and mis-scoped (b)): (a) H755/M4 `stm32f4x.cfg` — CONFIRMED BUG, but only
   in checked-in example `ArmDevelopmentEnvironment@19a3889:setup/
   create_project/dual/.vscode/launch.json:24-80` (all 4 configs use
   `interface/stlink.cfg` + `target/stm32f4x.cfg` for an H7 dual project);
   the generator `create_launch_json.sh:43-45,68-71` + tables in
   `stm_mcu_families.sh:29-75` are correct. (b) WL55JC using
   `stm32h7x_dual_bank.cfg` — CONFIRMED PRESENT (not refuted):
   `rust-embedded-environment@recover-branch:mcu-configs/stm32wl55jc.yml:18`
   (core 0) and `:30` uses `stm32f4x.cfg` (core 1); both wrong per finding 3
   (correct: `target/stm32wlx.cfg` + DUAL_CORE). Same pattern in
   `stm32h755.yml:30` (M4 core on `stm32f4x.cfg` — single-core-OK, wrong for
   dual sessions). Verify: `git -C ../rust-embedded-environment grep -n
   "stm32h7x_dual_bank\|stm32f4x\|stm32wlx" origin/recover-branch -- mcu-configs/`.
   (c) Swapped interface/target prompts — CONFIRMED (not refuted): the
   prompts live in the Rust templates, not the C++ CLI:
   `dual-core/cargo-generate.toml:11-12` (`openocd_interface_0` prompts
   "target configuration" defaulting to `stm32h7x_dual_bank.cfg`, a TARGET
   file; `openocd_target_0` prompts "interface configuration" defaulting to
   `stlink.cfg`, an INTERFACE file) and template `openocd.cfg:3-4` emits
   `interface/{{openocd_interface_0}}` + `target/{{openocd_target_0}}`,
   producing inverted paths. Same in `single-core/` files. Verify:
   `git -C ../rust-embedded-environment grep -n "openocd_interface_0\|openocd_target_0" origin/recover-branch -- "*.toml" "*.cfg"`.
5. Fork/version pin: `https://github.com/STMicroelectronics/OpenOCD.git`,
   branch `openocd-cubeide-r7` (default branch per repo page 2026-10-08);
   sibling `install_openocd.sh:3-9` clones branchless HEAD — pin to
   `openocd-cubeide-r7` + tag `v0.12.0` (latest tag per API 2026-10-08).
   Evidence: MISSING exact commit — run `git ls-remote` to pin SHA.

### Open

- O1: HW smoke test of all three cfgs with pinned OpenOCD (no probe here).
- O2: Decide per-pack policy: board cfg vs target cfg + DUAL_CORE flags,
  and WL single (stlink) vs dual-core (stlink-dap) session split.

## Recommendation

go-spec-pack — per-pack OpenOCD table (interface + board/target + flags)
for req-004; fix `dual/.vscode/launch.json` example + pin fork branch/tag
in spec. Timebox: ~2h of 3h used; stopped at findings, no implementation.
