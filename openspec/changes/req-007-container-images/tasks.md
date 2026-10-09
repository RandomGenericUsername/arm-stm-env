# Tasks

## 1. Dockerfiles

- [x] 1.1 `images/cpp.Dockerfile` (Debian slim digest-pinned, ARM GNU 15.3.rel2 gitlab host + checksum, ST OpenOCD fork @c8d973b built from source, versions recorded). Verify: pin grep empty; review against spike-003 table.
- [x] 1.2 `images/rust.Dockerfile` (rustup 1.99.0, both thumbv7em targets, probe-rs v0.32.0, ST OpenOCD fork, same pinning). Verify: pin grep empty.
- [x] 1.3 `images/README.md` (build commands, digest recording, CubeCLT gate + OPENs). Verify: commands + conditions present.

## 2. Lookup + checks

- [x] 2.1 Update lookup refs to pinned values; keep `pytest -k shim_lookup` green. Verify: suite green.
- [x] 2.2 Attempt builds iff Docker present (`docker --version`); else record skip with reason. Verify: either build logs or documented skip.
- [x] 2.3 `openspec validate` green + req-007 ticket update. Verify: exits 0; acceptance boxes checkable.
