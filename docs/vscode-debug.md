# Debugging in VS Code (container-attached)

How to build, flash, and debug a `mu`-generated project from VS Code, with the
window attached to a `mu` dev container. Covers single- and dual-core STM32
boards (NUCLEO-F411RE and NUCLEO-H755ZI-Q are the reference packs).

## 1. Generate a project

```sh
mu create --name my-project --mcu-config stm32f411re --lang c --vscode --path ~/Desktop
```

`--vscode` adds `.vscode/` (launch + tasks + settings + extension
recommendations), fetches the pack's pinned SVD(s) into `probe/`, and writes
`probe/probe-serial.cfg` (probe pinning — see §5).

## 2. Start the dev container

`mu dev` runs the pinned toolchain image interactively, with the project at
`/project` and the probe reachable:

```sh
mu dev --project-dir ~/Desktop/my-project        # interactive shell
```

The container gets the **whole USB bus** (`--device-cgroup-rule 'c 189:* rmw'`
+ `-v /dev/bus/usb`) rather than one device node, so replugging a board does not
break it, and `MU_PROBE_SERIAL` is set to the resolved probe's serial.

## 3. Attach VS Code

Command Palette → **Dev Containers: Attach to Running Container** → pick the
container → **Open Folder** → `/project`.

Tool paths are the in-container ones and are already wired in `.vscode/`:

| Tool | Path |
| --- | --- |
| GDB | `/opt/arm-gnu-toolchain/bin/arm-none-eabi-gdb` |
| OpenOCD | `/usr/local/bin/openocd` |

## 4. Build / flash / debug

**Tasks** (`Ctrl+Shift+B` runs the default *Build*; otherwise Palette → *Tasks: Run Task*):

| Task | Runs |
| --- | --- |
| Build | `make build` (all cores) |
| Clean | `make clean` |
| Flash | `make flash` (Clean → Build → program all cores) |
| Flash \<core\> | `make flash-<core>` (one core, e.g. the H755's M4 bank) |

**Launch configs** (Run and Debug panel, or `F5`):

| Config | What |
| --- | --- |
| `Debug <core> (OpenOCD)` | one core (dual-core packs get one per core) |
| `Debug <primary>+<sibling> (OpenOCD)` | both cores at once (chained; sibling nested in the Call Stack) |

**Keys** (VS Code defaults; nothing is remapped): `F5` start/continue ·
`Shift+F5` stop · `Ctrl+Shift+F5` restart · `F9` breakpoint · `F10` step over ·
`F11` step into · `Shift+F11` step out.

The **Peripherals** view uses the pack's SVD (register names per core). The
**Watch** panel is the quickest way to see a sibling core working — the
generated sibling example counts a `volatile uint32_t counter`.

**Ending a session:** use **Disconnect** (not Stop) to leave the firmware
running — a generated `probe/resume-on-detach.cfg` resumes the target on detach.

## 5. How the probe is chosen

The container sees every attached probe, so the probe is selected by **serial**:

- `mu` resolves the probe on the host (`--serial`, `--vid/--pid`, an explicit
  `--device`, or auto-detect when exactly one is attached) and sets
  `MU_PROBE_SERIAL` in the container.
- `probe/probe-serial.cfg` (included by the Makefile flash targets and by
  `launch.json`) turns that into `adapter serial <serial>`.
- Unset/empty ⇒ OpenOCD picks the only probe.

With two boards attached and no selector, `mu` refuses to guess:

```
mu: error: 2 probes attached (0483:3754(…), 0483:3752(…)); pass --serial or --vid/--pid
```

## 6. Expected behaviour (not bugs)

- **The LED blinks at ~2 Hz.** The generated delay is calibrated for a visible
  rate; a very fast blink reads as "steady on".
- **Step *over* the delay loop, don't step into it.** `delay_half_period()` /
  `delay_loop()` run ~10^5–10^6 NOP iterations, so `F11` into it appears stuck;
  `F10` skips it.
- **Sibling cores run a counter**, not the LED — the example drives the
  on-board LED on the primary core only.

## 7. Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `GDB Server Quit Unexpectedly` | container can't open the probe: stale device binding (pre-`bug-018`) or the board is unplugged. Recreate the container (`mu dev`) so it re-resolves. |
| `Protocol error with Rcmd: 01` on launch | `cortex_m maskisr` was emitted for an **HLA** pack (`stlink.cfg`). Fixed by `bug-016`; regenerate the project. |
| `make: …: No such file or directory` / `Error 127` | login shell lost the toolchain PATH. Fixed by `bug-017`; needs an image rebuild (`make images`) or a container with the fix. |
| Debug attaches but the source/step looks wrong | dual-core: the config attached to the wrong core. Fixed by `bug-013` (per-core `targetProcessor`); regenerate. |
| Stepping never advances (H7) | `bug-011`: needs `monitor cortex_m maskisr steponly` (DAP only); regenerate. |

Regenerating means re-running `mu create --vscode` (or copying the updated
`.vscode/` + `probe/` files) — the fixes live in the generator, not in the
project.

## 8. Without VS Code

```sh
mu build --project-dir ~/Desktop/my-project
mu flash --project-dir ~/Desktop/my-project --serial <probe-serial>
mu debug --project-dir ~/Desktop/my-project --serial <probe-serial>
```

See also: `docs/flash-stm32-linux.md` (raw OpenOCD / USB access),
`docs/e2e-evidence.md` (how the flash paths are proven).
