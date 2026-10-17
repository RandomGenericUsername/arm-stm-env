---
id: spike-003
title: "2026 toolchain recon"
kind: spike
status: done
parent: epic-001
timebox: "3h"
links:
  openspec: none
  bmad: []
worktree: ""
branch: ""
---

## Questions

1. Current versions, URL schemes, and license/terms for: ARM GNU toolchain, Rust + embedded targets, ST OpenOCD fork, STM32CubeCLT, probe-rs, esptool, avrdude?
2. CubeCLT vs vanilla GCC verdict for images?

## Findings

### Answered

1. ARM GNU: old `developer.arm.com/downloads/-/arm-gnu-toolchain-downloads` is DEAD — HTTP 301 → `https://gitlab.arm.com/tooling/gnu-toolchains-for-arm` (curl -sSI, 2026-10-08). New home branch tip `main=a7d342b`; latest release branch `releases/15.3.rel2` (git ls-remote --heads, sorted). Siblings' `12.3.rel1` branch still listed but superseded. Checksums on new host: UNVERIFIED (OPEN).
2. Rust: stable **1.99.0** (`b940084d7 2026-09-28`, channel date 2026-10-01, static.rust-lang.org channel toml). `thumbv7em-none-eabi/-eabihf` both Tier-2 no_std (`*`, "Bare Armv7E-M") per doc.rust-lang.org platform-support. Channel toml lists both targets' llvm-tools. probe-rs **v0.32.0** (2026-07-22, github releases/latest). flip-link **v0.1.12**, cargo-generate **v0.25.0** (github releases/latest, dates shown w/o year).
3. ST OpenOCD fork: `openocd-cubeide-r7 = c8d973bdad9a6fddb51459eda109b3b95d23b57a`; tag `v0.12.0 = 5cc204e` (peeled `9ea7f3d`) — git ls-remote 2026-10-08. v0.12.0 tag CONFIRMED present.
4. STM32CubeCLT: **RESOLVED 2026-10-16** (was UNVERIFIED — st.com unreachable from this net; webfetch timeout + curl http1.1 timeout 2026-10-08, repeated 2026-10-09 `curl --max-time 20` → `000`). Version **1.22.0**; SLA0048 `<https://www.st.com/resource/en/license/SLA0048_STM32CubeCLT.pdf>` — redistribution **permitted with conditions** (clause 2: reproduce copyright/conditions/disclaimer in capital type in the distribution docs; clause 4: solely with ST processing units; clause 5: not subject to Open Source Terms; clause 11: non-conforming redistribution is void). Download is MyST/email-gated with 24h links — there is **no stable public URL by design**. Verdict in `tickets/req-027-cubeclt-verdict/ticket.md`: exclude from images (practical, not legal), optional as a host-side tool. Caveat: the ST pages/PDF were read through a reader proxy (one hop) because st.com is unreachable from here.
5. esptool **v5.5.0** (2026-10-08) home github.com/espressif/esptool; avrdude **v8.3** home github.com/avrdudes/avrdude (releases/latest pages).

### Open

- ARM 15.x checksums/sidebar T&Cs on new gitlab host (checksums since
  closed — `.sha256asc` sidecar; sidebar T&Cs still open).
- ~~CubeCLT version + SLA redistribution terms + stable download URL~~ —
  **CLOSED 2026-10-16** in `req-027` (see finding 4). Note: the framing was
  wrong — redistribution is permitted-with-conditions, not forbidden.

## Recommendation

Ship images on **vanilla ARM GNU (new gitlab host)** over CubeCLT: public no-login fetch, branch-pinned reproducibility, no redistribution encumbrance observed. CubeCLT excluded by decision (`req-027`, 2026-10-16) — on practical grounds (login/EULA-gated download, no capability the images lack, older GCC), **not** because redistribution is forbidden. CubeCLT remains optional as a host-side auxiliary/diagnostics tool.
