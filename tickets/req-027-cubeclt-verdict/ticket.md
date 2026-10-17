---
id: req-027
title: "STM32CubeCLT verdict"
kind: requirement
status: done
size: S
lane: bmad-advisory
parent: epic-002
links:
  openspec: none
  bmad: []
worktree: .worktrees/req-027/
branch: ticket/req-027-cubeclt-doc-closeout
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
open thread closed, `spike-003` UNVERIFIED note resolved. — **Met 2026-10-16.**

## Doc-closeout evidence (2026-10-16)

Branch `ticket/req-027-cubeclt-doc-closeout`, worktree `.worktrees/req-027/`
(from main `852e508`). Files propagated, all in commit
`docs(req-027): propagate the CubeCLT verdict into the docs`:

- `images/README.md` — section retitled "CubeCLT — EXCLUDED by decision (vanilla
  wins); optional host tool"; the old "until license/redistribution proof are
  recorded" framing is gone (it was wrong: redistribution is
  permitted-with-conditions). CLAUSES 2/4/5/11 + the SLA0048 URL are now cited
  inline, the one-hop reader-proxy caveat is noted, and the OPEN item
  "CubeCLT version + SLA redistribution terms + stable download URL" is ticked
  with version 1.22.0 and the MyST/email-gated (no stable public URL) finding.
- `HANDOFF.md` — the "CubeCLT verdict (st.com unreachable)" open thread is
  resolved → `req-027`. Stale-and-resolved items in the same list corrected:
  HW flash/run → `ops-027`/`ops-028`, IDE attach → `req-016`, registry push →
  `ops-030`; warnings policy kept but now points at `ops-033`; registry
  visibility kept as the live thread → `ops-034`. The epic-001 bullet's
  "no probe has ever touched silicon" claim is marked superseded.
- `tickets/spike-003-toolchain-recon/ticket.md` — finding 4 rewritten from
  "UNVERIFIED … all OPEN" to the resolved facts (1.22.0, SLA0048
  permitted-with-conditions, login/EULA-gated download); the Open-list entry
  struck through as CLOSED; the Recommendation corrected to say the exclusion
  is practical, not legal.
- `tickets/req-007-container-images/ticket.md` — acceptance item
  "CubeCLT-vs-GCC decision recorded" ticked with a `Verify:` command.
- `tickets/INDEX.md` — both req-027 entries (epic-002 nested line + Requirements)
  flipped to `done`.

Evidence: the edits above. Verify: `git -C .worktrees/req-027 show --stat HEAD`
and `rg -n "SLA0048" images/README.md tickets/spike-003-toolchain-recon/ticket.md`.