# Spec Delta

## Purpose

CLI verbs are pure orchestration over the certified model: each verb loads, validates, hands to an adapter port, and renders a verdict — with no device conditionals anywhere in `cli/`.

## ADDED Requirements

### Requirement: Verbs carry no hardware knowledge

No file under `engine/cli/` SHALL branch on device family, chip, or backend name. All device behavior arrives via the model + adapter ports.

Evidence: AD-6 rule text. Verify: `rg -i "stm32|esp32|avr|openocd|esptool|avrdude" engine/cli/` empty.

#### Scenario: New brand without CLI edits

- **WHEN** a fourth chip family ships (adapter + pack only)
- **THEN** zero files under `engine/cli/` change (review gate)

### Requirement: Shim resolves language to image identically in both modes

The shim SHALL map `--lang` to image via the core-owned lookup and exec the verb in that image whether invoked on a bare host or inside the container.

Evidence: AD-8. Verify: lookup unit test maps c/cpp/rust to expected image refs; shim dry-run prints identical container args both modes.

#### Scenario: Same image both modes

- **WHEN** `build` runs on bare host vs inside container
- **THEN** the resolved image reference is identical

### Requirement: Probe mapping stays in the shim

Per-OS probe endpoint preparation SHALL live in shim code only; core/adapters receive the prepared endpoint struct.

Evidence: AD-9. Verify: `rg -i "/dev/|vid|pid" engine/core/ engine/adapters/ 2>/dev/null` empty (populated later stories); shim mapping tested with fixture requirements.

#### Scenario: macOS quirk contained

- **WHEN** a macOS-specific mapping rule exists
- **THEN** it lives in shim code and no core/adapter file mentions the OS

### Requirement: Flash renders one verdict from multi-piece results

`flash` SHALL collect per-piece adapter results + proof payload and render a single verdict (n/n pieces OK + proof rung outcome).

Evidence: AD-6/AD-10. Verify: stub-adapter test with 3-piece ESP-style result renders `3/3 OK` + rung.

#### Scenario: Partial flash failure

- **WHEN** 2 of 3 pieces succeed and proof fails on the third
- **THEN** the verdict reads failure, names the failed piece, and carries no proof claim
