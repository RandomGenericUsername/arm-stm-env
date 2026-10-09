# Container images

One image per toolchain family. Every toolchain reference is pinned: base image
digest, toolchain version + source URL + checksum, OpenOCD fork SHA.

## Pins (recorded 2026-10-09)

| Item | Pin | Evidence |
|---|---|---|
| Base | `debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587` | `docker pull debian:bookworm-slim` + `docker inspect` |
| ARM GNU | 15.3.rel2, `.../packages/generic/gnu-toolchain/15.3.rel2/arm-gnu-toolchain-15.3.rel2-x86_64-arm-none-eabi.tar.xz`, sha256 `0662b2f0…7874e` | README.md on `releases/15.3.rel2` branch lists generic-packages URLs; `.sha256asc` fetched via curl (full hash in Dockerfiles) |
| ARM branch head | `releases/15.3.rel2 = 601782f` | `git ls-remote --heads https://gitlab.arm.com/tooling/gnu-toolchains-for-arm.git` |
| OpenOCD fork | `c8d973bdad9a6fddb51459eda109b3b95d23b57a` (= HEAD of `openocd-cubeide-r7`, tag `openocd-cubeide-v2.2.0`) | `git ls-remote https://github.com/STMicroelectronics/OpenOCD.git` |
| Rust | 1.99.0 (`b940084d7 2026-09-28`) | `pkg.rust` version in `https://static.rust-lang.org/dist/channel-rust-stable.toml` |
| probe-rs | v0.32.0, `probe-rs-tools-x86_64-unknown-linux-gnu.tar.xz`, sha256 `c2ccc460…851ff5` | release asset `.sha256` fetched via curl |
| flip-link | 0.1.12 | `cargo install --locked --version 0.1.12` |
| rustup-init | sha256 `dda72343…c9fcb71` observed 2026-10-09 | `rustup-init.sha256` sidecar; Dockerfile verifies sidecar + recorded pin |

## Build

```sh
docker build --platform linux/amd64 -f images/cpp.Dockerfile  -t ghcr.io/arm-stm-env/lang-cpp:15.3.rel2 images/
docker build --platform linux/amd64 -f images/rust.Dockerfile -t ghcr.io/arm-stm-env/lang-rust:1.99.0 images/
docker inspect ghcr.io/arm-stm-env/lang-cpp:15.3.rel2  --format='{{.RepoDigests}}'
docker inspect ghcr.io/arm-stm-env/lang-rust:1.99.0    --format='{{.RepoDigests}}'
```
(Prefer `make images` / `make digests` — same commands, parameterized.)

Record the resulting digests here after each build (base-image updates change
them; re-record, do not silently float).

Built digests (2026-10-09, `FROM --platform=linux/amd64`, Docker 29.8.2):
- cpp: `arm-stm-env/lang-cpp:15.3.rel2 @ sha256:27d29e05159fc71ddb6a2218de653ad401786cd81163cfcba86948642fa3a50d` (2.02GB, amd64).
- rust: `arm-stm-env-lang-rust:1.99.0 @ sha256:814093c2800a7ab6db48e52af71146ae09189d1bc7a810b7ac4416cb15c60c56` (amd64). Smoke: rustc 1.99.0 (b940084d7), probe-rs 0.32.0, both thumbv7em targets, OpenOCD c8d973bda.
  Smoke: `rustc 1.99.0 (b940084d7)`, both thumbv7em targets, `probe-rs 0.32.0`,
  flip-link in cargo bin, OpenOCD `0.12.0+dev-00664-gc8d973bda`.

Note: `FromPlatformFlagConstDisallowed` lint warning on `FROM
--platform=linux/amd64` is intentional (x86_64-only toolchain tarballs) — keep.

## Pin audit

```sh
rg -i "latest|:stable" images/*.Dockerfile   # must print nothing (exit 1)
```

## CubeCLT gate (still CLOSED — vanilla wins)

`https://www.st.com/en/development-tools/stm32cubeclt.html` unreachable from
this net (curl `--max-time 20` → `000`, 2026-10-09; same verdict as spike-003
on 2026-10-08). Until version + stable URL + license/redistribution proof are
recorded, images ship **vanilla ARM GNU from the public gitlab host**
(no login, branch-pinned, no redistribution encumbrance observed).

## OPENs carried from spike-003

- [x] ARM 15.x checksums on new gitlab host — CLOSED: `.sha256asc` sidecar
      reachable via generic-packages API, hash recorded above.
- [ ] ARM sidebar T&Cs on new host — still OPEN (EULA.txt exists in branch;
      redistribution terms not reviewed).
- [ ] CubeCLT version + SLA redistribution terms + stable download URL —
      still OPEN (st.com unreachable twice).
