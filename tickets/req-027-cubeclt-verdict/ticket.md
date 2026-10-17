---
id: req-027
title: "STM32CubeCLT verdict"
kind: requirement
status: in-progress
size: S
lane: bmad-advisory
parent: epic-002
links:
  openspec: none
  bmad: []
worktree: .worktrees/ops-035/
branch: ticket/ops-035-triage-findings
---

# STM32CubeCLT verdict

## Verdict (2026-10-16)

**EXCLUDE CubeCLT from the pinned images (default); list it OPTIONAL as a
host-side auxiliary/diagnostics tool.**

1. **Redistributable, but conditional (SLA0048).** Clause 2 (binary redistribution
   must reproduce the copyright/conditions/disclaimer *in capital type* in the
   image's docs), clause 4 (*solely* on ST processing units), clause 5 (must **not**
   subject CubeCLT to Open Source Terms), clause 11 (non-conforming = void). So it
   *can* be baked into a public OCI image, but not unconditionally.
   Evidence: `https://www.st.com/resource/en/license/SLA0048_STM32CubeCLT.pdf`
   (fetched through a reader proxy — st.com is unreachable from here, see below).
   Note: **this corrects the framing** — it is gated on *conditions*, not forbidden.
2. **Breaks the no-login reproducible build.** Installer needs manual license
   acceptance; download is MyST/email-gated (24h links) — incompatible with the
   repo's pinned public no-login fetch (`spike-003-toolchain-recon/ticket.md:36`).
3. **Adds no needed capability.** Its GCC (14.3) is *older* than the pinned
   vanilla 15.3.rel2 (`images/cpp.Dockerfile:7`); **CubeCLT does not ship OpenOCD**
   (so the ST OpenOCD fork is still required); SVDs already come from modm-io
   (Apache-2.0, pinned). The one real gap — ST-LINK firmware update — is already a
   documented CubeProgrammer-GUI step (`docs/flash-stm32-linux.md:89`).

Verify: `rg -n "CubeCLT|ARM_GCC_VERSION|OPENOCD_SHA" images/cpp.Dockerfile` →
no CubeCLT dependency; vanilla 15.3.rel2 + OpenOCD fork `c8d973b`.

## Done-when

Verdict recorded with evidence, `images/README.md` gate updated, `HANDOFF.md`
open thread closed, `spike-003` UNVERIFIED note resolved. (Docs update dispatched.)