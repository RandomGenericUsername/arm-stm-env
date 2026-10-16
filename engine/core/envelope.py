"""The operational envelope (task-012, AD-17) — the one owned place.

Everything the framework assumes about *where it runs* is named here, so a lane,
an error message, or a test can point at one definition instead of a literal
scattered across the tree:

- **container runtime** — the CLI binary invoked for ``auto`` mode, and the
  platform the pinned images are built for;
- **host tools** — what ``create`` needs on the host PATH (``git``; network
  access for vendoring);
- **probe access** — the sysfs root the shim enumerates for USB probes, the
  ``/dev/bus/usb`` tree passed through, and the container cgroup rule that
  permits character device 189:* (AD-9).

**Deferred lanes** (not supported, and deliberately not designed out): a Windows
native lane; any container runtime other than Docker (podman, nerdctl); and
images for platforms other than :data:`CONTAINER_PLATFORM`. A lane needing a
different envelope is an explicit item, never an undocumented assumption.
"""

from __future__ import annotations

__all__ = [
    "CONTAINER_PLATFORM",
    "CONTAINER_RUNTIME",
    "HOST_GIT",
    "SYSFS_USB",
    "USB_BUS_ROOT",
    "USB_CGROUP_RULE",
]

#: Container CLI used for ``auto`` mode (images carry the toolchains).
CONTAINER_RUNTIME = "docker"

#: Platform the pinned toolchain images are built for (e2e runs it explicitly).
CONTAINER_PLATFORM = "linux/amd64"

#: Host tool ``create`` needs for vendoring (plus network to the pinned remotes).
HOST_GIT = "git"

#: sysfs root the shim enumerates to resolve a USB probe (AD-9).
SYSFS_USB = "/sys/bus/usb/devices"

#: Host USB tree passed into the container as a volume.
USB_BUS_ROOT = "/dev/bus/usb"

#: cgroup rule admitting character device 189:* (USB) so a replug survives.
USB_CGROUP_RULE = "c 189:* rmw"
