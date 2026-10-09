---
id: spike-004
title: "Per-project config-header flow (lwipopts.h-style)"
kind: spike
status: reporting
parent: epic-001
timebox: "2h"
links:
  openspec: none
  bmad: []
worktree: .worktrees/spike-004/
branch: ticket/spike-004-config-headers
---

## Questions

1. How do per-project config headers (e.g. lwIP `lwipopts.h`, mbedTLS `mbedtls_config.h`) flow through packs/templates: who authors the defaults, where do user overrides live, and what build mechanism selects them?
2. How does this compose with the spike-002 vendoring pick (vendored sources + local config headers)?

## Findings

### Answered

1. **lwIP canonical mechanism = app-supplied `lwipopts.h` on the include path.** `opt.h` does `#include "lwipopts.h"` first: "Include user defined options first. Anything not defined in these files will be set to standard values." App never edits `opt.h`; port supplies `lwipopts.h` via `-I`.
   - Evidence: https://raw.githubusercontent.com/lwip-tcpip/lwip/master/src/include/lwip/opt.h — "Include user defined options first. Anything not defined in these files will be set to standard values."
   - Verify: `curl -s <url> | head -50`
2. **mbedTLS canonical mechanism = `-D` config-file selectors, not editing the tree.** `mbedtls_config.h` documents `MBEDTLS_CONFIG_FILE` ("a header which will be included instead of `"mbedtls/mbedtls_config.h"`… must be defined on the compiler command line") and `MBEDTLS_USER_CONFIG_FILE` ("included after… This allows you to modify the default configuration, including the ability to undefine options"). Replace vs overlay, both via command line.
   - Evidence: https://raw.githubusercontent.com/Mbed-TLS/mbedtls/development/include/mbedtls/mbedtls_config.h — quotes above.
   - Verify: `curl -s <url> | grep -A6 MBEDTLS_CONFIG_FILE`
3. **Zephyr = Kconfig merge (board `_defconfig` + app `prj.conf`), output generated `autoconf.h`.** "The initial configuration… comes from merging… `<BOARD>_defconfig`… The application configuration… `prj.conf`… If a symbol is assigned both…, the value set in the application configuration takes precedence." Invisible symbols only via `Kconfig.defconfig`, never `.config`.
   - Evidence: https://docs.zephyrproject.org/latest/build/kconfig/setting.html — quotes above.
   - Verify: `webfetch <url> (Setting Kconfig configuration values)`
4. **PlatformIO = per-project `platformio.ini`, per-env `build_flags` (`-D`/`-I`/`-include`).** "Each PlatformIO project has its own `platformio.ini`… in the root directory"; `build_flags` maps `-D name`→CPPDEFINES, `-Idir`→CPPPATH, `-include file`→CCFLAGS.
   - Evidence: https://docs.platformio.org/en/latest/projectconf/index.html ("Each PlatformIO project has its own platformio.ini…"); https://docs.platformio.org/en/latest/projectconf/sections/env/options/build/build_flags.html (scope table).
   - Verify: `webfetch` both URLs.

### Open

- None blocking req-004. Detail deferred: exact `--config`/project-file schema and generated-header vs `-include` choice (decide in spec).

## Recommendation

Pack authors ship default config headers per lib; template generates a per-project `config/` dir (defaults copied, user-owned); user overrides live in project file / pack section rendered into that dir; build wires via include-path order (`-I config/` first) + `-DMBEDTLS_CONFIG_FILE`/`_USER_CONFIG_FILE`-style selectors; no Kconfig-lite — one static generated header per build. Composes with disciplined vendoring: submodule trees stay pristine, all config headers live outside them.
