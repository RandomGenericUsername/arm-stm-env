---
id: ops-014
title: "Vendoring: partial+sparse clone (create in seconds, not minutes)"
kind: ops-task
status: done
lane: direct
links:
  openspec: none
  bmad: none
worktree: .worktrees/ops-014/
branch: ticket/ops-014-sparse-vendor
---

# Vendoring: partial+sparse clone (create in seconds, not minutes)

> `ops-task`; no `parent:`.

## Work

`mu create` took minutes because vendoring did a **full clone of CMSIS_5**
(~133 MB tree; only `CMSIS/Core` ~3 MB is referenced). Replace `git submodule
add` with a **partial + sparse shallow clone** per pin:

```
git clone --filter=blob:none --sparse --depth 1 --branch <tag> <url> <dest>
git -C <dest> sparse-checkout set <subtree>          # CMSIS: CMSIS/Core; device: Include Source
git config -f .gitmodules submodule.<dest>.{path,url} …
git … add .gitmodules <dest>
git … submodule absorbgitdirs <dest>                 # native submodule gitdir
git … submodule init <dest>
```

Consumes `engine/templates/vendoring.py` (`_add_pin` gains a `sparse` arg;
`CMSIS_SPARSE`/`FAMILY_SPARSE`). Tests updated to the new mechanism.

## Evidence

Measured 2026-10-14 (F411RE/C):

| | before | after |
|---|---|---|
| `create` wall time | minutes | **4 s** |
| `vendor/CMSIS` | 133 MB | **4.7 MB** |
| submodule status | `2b7495b… (5.9.0)` | same (native) |

Verify: `mu create --mcu-config stm32f411re --lang c --name demo --path <fresh>`
then `mu build --project-dir <fresh>/demo` → ELF (`text=872`). `make test` → 237 passed.

## Done-when

Fresh `create` is seconds, the pinned submodules are native (`git submodule
status`), and the rendered project still builds.
