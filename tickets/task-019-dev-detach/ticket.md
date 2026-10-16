---
id: task-019
title: "mu dev --detach: start an attachable, long-running dev container"
kind: task
status: done
lane: inherits
parent: req-022
links:
  openspec: none
  bmad: none
worktree: .worktrees/task-019/
branch: ticket/task-019-dev-detach
---

# mu dev --detach: start an attachable, long-running dev container

## Parent

`req-022` — lane inherited from parent.

## Work

An editor attaches to a container that is **already running**. `mu dev` starts an
interactive shell (`-it … /bin/bash`) whose container dies with its terminal, so
attaching needed a hand-written `docker run -d … sleep infinity` — including the
toolchain-env fix-up by hand.

Add `mu dev --detach`: same image, mounts and probe forwarding, but `-d --name
mu-dev-<project>`, a liveness process, and a wait until a shell inside resolves
the stack's build tool.

The toolchain-env problem is general: an exec'd shell (what an editor opens) never
runs the image's ENTRYPOINT. Images that set their toolchain on PATH need nothing;
the ESP-IDF image enables it in its entrypoint, so `StackSpec` gains an
`env_setup` fragment that the detach command installs into `/etc/profile.d` +
`/root/.bashrc` — login **and** interactive shells.

## Done-when

`mu dev --detach` yields a named, attachable container whose shells have the
toolchain; interactive `mu dev` is unchanged; `make test` green.

## Evidence

2026-10-16 — branch `ticket/task-019-dev-detach`:

```
mu dev --detach --project-dir ~/Desktop/esp32cam --device /dev/ttyUSB0
docker run -d --name mu-dev-esp32cam --device /dev/ttyUSB0:/dev/ttyUSB0 … \
  espressif/idf:v6.1@sha256:81893c71… bash -lc '…zz-mu-env…; exec sleep infinity'
→ dev container 'mu-dev-esp32cam' is running and attachable.
  VS Code: Command Palette -> Dev Containers: Attach to Running Container
```

- Immediately after the command returns (it waits for readiness, ~3 s):
  `docker exec mu-dev-esp32cam bash -ic 'idf.py --version'` → `ESP-IDF v6.1`
  (login and interactive shells both).
- Before the readiness wait, the same exec raced the entrypoint and reported
  `idf.py: command not found` — hence `_wait_dev_ready()`.
- `make test` → **354 passed** (7 new tests: `-d`/`--name`, no `-it`/`--rm`, the
  liveness + env command, `--detach` without a name, the mount preflight not
  detaching, interactive `dev` unchanged, name derivation).
- `docs/vscode-debug.md` §2 documents both forms.

Notes: the container is **not** `--rm`, so a stopped one can be restarted, and
`mu dev --detach` replaces any previous container of the same name.