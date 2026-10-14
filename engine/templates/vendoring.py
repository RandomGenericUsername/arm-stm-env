"""Pinned CMSIS submodule vendoring (req-011).

``vendor(pack_id, project_dir)`` registers two pinned submodules in an
already-rendered C/C++ project tree: CMSIS core at ``vendor/CMSIS`` and the
family device repo at ``vendor/cmsis-device-<pack-id>``. If the project dir is
not already inside a git work tree, ``git init`` runs there first (so `create`
works in a fresh/empty directory); a dir already inside a work tree (e.g. a
monorepo) is left alone.

Mechanism (req-011, ops-014): each pin is a partial (blob-filtered) + sparse
shallow clone at the tag — ``git clone --filter=blob:none --sparse --depth 1
--branch <tag>`` + ``git sparse-checkout set <subtree>`` — then registered in
``.gitmodules`` + the index and made a native submodule via ``submodule
absorbgitdirs``/``init``. Only the referenced subtree is downloaded (CMSIS_5 is
~133 MB full, ~3 MB for CMSIS/Core). Tags are immutable so pins are
reproducible. Every failure raises :class:`VendorError` naming the missing
capability/path/URL — never a half-vendored tree.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

__all__ = [
    "PINS",
    "FAMILY_REPOS",
    "VENDOR_CORE_PATH",
    "VendorError",
    "family_repo",
    "vendor",
]

CMSIS_CORE_URL = "https://github.com/ARM-software/CMSIS_5.git"
CMSIS_CORE_TAG = "5.9.0"
VENDOR_CORE_PATH = "vendor/CMSIS"

# Family device repos, verified 2026-10-13 (ls-remote tags + HTTP 200 on
# core header, device Include header, and gcc startup file per family).
FAMILY_REPOS = {
    "f4": ("https://github.com/STMicroelectronics/cmsis_device_f4.git", "v2.6.9"),
    "h7": ("https://github.com/STMicroelectronics/cmsis_device_h7.git", "v1.9.0"),
    "wl": ("https://github.com/STMicroelectronics/cmsis_device_wl.git", "v1.4.0"),
}

# Pin table: logical name -> (repo URL, tag). Kept as the single source the
# tests assert against (spec: pins recorded as tag SHAs, not branches).
PINS = {
    "CMSIS_5": (CMSIS_CORE_URL, CMSIS_CORE_TAG),
    **{f"cmsis_device_{fam}": pin for fam, pin in FAMILY_REPOS.items()},
}


class VendorError(RuntimeError):
    """Loud vendoring failure: names the missing capability, path, or URL."""


def _family_of(pack_id: str) -> str:
    """Family key from the pack id prefix (``stm32f4…`` -> ``f4``)."""
    for fam in FAMILY_REPOS:
        if pack_id.startswith(f"stm32{fam}"):
            return fam
    raise VendorError(
        f"vendoring: unknown family for pack id {pack_id!r}; "
        f"expected one of {sorted('stm32' + f for f in FAMILY_REPOS)}"
    )


def family_repo(pack_id: str) -> tuple[str, str, str]:
    """(repo URL, tag, submodule path) for the pack's family device repo."""
    fam = _family_of(pack_id)
    url, tag = FAMILY_REPOS[fam]
    return url, tag, f"vendor/cmsis-device-{pack_id}"


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


#: Subtrees each pinned repo actually contributes, so a partial+sparse clone
#: fetches only what the build references (ops-014).
CMSIS_SPARSE = ("CMSIS/Core",)
FAMILY_SPARSE = ("Include", "Source")


def _git_ok(args: list[str], cwd: Path, what: str) -> None:
    done = _run_git(args, cwd)
    if done.returncode != 0:
        raise VendorError(
            f"vendoring: `{' '.join(args)}` failed in {cwd} ({what}): "
            f"{done.stderr.strip()}"
        )


def _add_pin(
    url: str, tag: str, dest: str, project_dir: Path, sparse: tuple[str, ...]
) -> None:
    """Vendor one pinned repo as a submodule, downloading only ``sparse`` paths.

    Partial (blob-filtered) + sparse shallow clone at ``tag``, registered in
    ``.gitmodules`` + the index, then migrated into ``.git/modules`` and marked
    initialized — the native ``git submodule add`` state, minus the full tree.
    """
    done = _run_git(
        [
            "git", "clone", "--filter=blob:none", "--sparse", "--depth", "1",
            "--branch", tag, url, dest,
        ],
        project_dir,
    )
    if done.returncode != 0:
        raise VendorError(
            f"vendoring: `git clone` of {url}@{tag} failed in {project_dir} "
            f"(network required at create time; unreachable remote or moved tag "
            f"→ no partial tree): {done.stderr.strip()}"
        )
    _git_ok(
        ["git", "-C", dest, "sparse-checkout", "set", *sparse],
        project_dir,
        f"cannot select the {sparse} subtree of {url}@{tag}",
    )
    gitmodules = str(project_dir / ".gitmodules")
    for key, value in (("path", dest), ("url", url)):
        _git_ok(
            ["git", "-C", str(project_dir), "config", "-f", gitmodules,
             f"submodule.{dest}.{key}", value],
            project_dir,
            "cannot record the pin",
        )
    _git_ok(
        ["git", "-C", str(project_dir), "-c", "advice.addEmbeddedRepo=false",
         "add", ".gitmodules", dest],
        project_dir,
        "cannot record the pinned gitlink",
    )
    _git_ok(
        ["git", "-C", str(project_dir), "submodule", "absorbgitdirs", dest],
        project_dir,
        "cannot migrate the submodule git dir",
    )
    _git_ok(
        ["git", "-C", str(project_dir), "submodule", "init", dest],
        project_dir,
        "cannot initialize the submodule",
    )


def _ensure_repo(out: Path) -> None:
    """Make ``out`` a git work tree so submodule vendoring can run.

    Idempotent: a path already inside a work tree (e.g. a monorepo) is left
    untouched; otherwise ``git init`` runs in ``out``. Failure is loud.
    """
    probe = _run_git(["git", "-C", str(out), "rev-parse", "--is-inside-work-tree"], out)
    if probe.returncode == 0 and probe.stdout.strip() == "true":
        return
    init = _run_git(["git", "init"], out)
    if init.returncode != 0:
        raise VendorError(
            f"vendoring: `git init` failed in {out} (cannot create the project "
            f"repo that `git submodule add` needs): {init.stderr.strip()}"
        )


def vendor(pack_id: str, project_dir: str | Path) -> list[Path]:
    """Register pinned CMSIS submodules; return the submodule dirs.

    Runs ``git init`` in a project dir that is not already inside a work tree.
    Raises :class:`VendorError` (non-zero create path) when git is missing, the
    project dir does not exist, the family is unknown, or any git step fails
    (e.g. offline: unreachable remote URL named in the message).
    """
    out = Path(project_dir)
    if not out.is_dir():
        raise VendorError(
            f"vendoring: out-dir {out} does not exist; render the project first"
        )
    if shutil.which("git") is None:
        raise VendorError(
            "vendoring: `git` not found on PATH; install git and re-run create "
            "(submodule init requires the git CLI on the host)"
        )
    _ensure_repo(out)
    _add_pin(CMSIS_CORE_URL, CMSIS_CORE_TAG, VENDOR_CORE_PATH, out, CMSIS_SPARSE)
    url, tag, dest = family_repo(pack_id)
    _add_pin(url, tag, dest, out, FAMILY_SPARSE)
    return [out / VENDOR_CORE_PATH, out / dest]
