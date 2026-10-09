# C/C++ image: vanilla ARM GNU Toolchain + ST OpenOCD fork, Debian bookworm-slim.
# Pinned: base digest, ARM GNU 15.3.rel2 (new gitlab host, sha256-verified),
# OpenOCD fork SHA c8d973b built from source. No CubeCLT (gated, see README).
# Toolchain tarballs below are x86_64-only, so the image platform is pinned too.
FROM --platform=linux/amd64 debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587

ARG ARM_GCC_VERSION=15.3.rel2
ARG ARM_GCC_SHA256=0662b2f01e0cd8b951fd110911d339c35b05998c68a12b3530bbbb4bf6c7874e
ARG ARM_GCC_URL=https://gitlab.arm.com/api/v4/projects/tooling%2Fgnu-toolchains-for-arm/packages/generic/gnu-toolchain/15.3.rel2/arm-gnu-toolchain-15.3.rel2-x86_64-arm-none-eabi.tar.xz
ARG OPENOCD_REPO=https://github.com/STMicroelectronics/OpenOCD.git
ARG OPENOCD_SHA=c8d973bdad9a6fddb51459eda109b3b95d23b57a

LABEL org.arm-stm-env.arm-gcc.version="15.3.rel2" \
      org.arm-stm-env.arm-gcc.sha256="0662b2f01e0cd8b951fd110911d339c35b05998c68a12b3530bbbb4bf6c7874e" \
      org.arm-stm-env.openocd.repo="https://github.com/STMicroelectronics/OpenOCD.git" \
      org.arm-stm-env.openocd.sha="c8d973bdad9a6fddb51459eda109b3b95d23b57a" \
      org.arm-stm-env.base="debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587"

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/arm-gnu-toolchain/bin:/usr/local/bin:${PATH}

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl xz-utils \
        build-essential git autoconf automake libtool pkg-config make \
        libusb-1.0-0-dev libhidapi-dev libudev-dev \
    && rm -rf /var/lib/apt/lists/*

# ARM GNU toolchain: download + sha256 verify + extract to /opt.
RUN curl -fsSL -o /tmp/arm-gnu.tar.xz "${ARM_GCC_URL}" \
    && echo "${ARM_GCC_SHA256}  /tmp/arm-gnu.tar.xz" | sha256sum -c - \
    && mkdir -p /opt/arm-gnu-toolchain \
    && tar -xf /tmp/arm-gnu.tar.xz -C /opt/arm-gnu-toolchain --strip-components=1 \
    && rm /tmp/arm-gnu.tar.xz \
    && arm-none-eabi-gcc --version | head -1

# ST OpenOCD fork from source at pinned SHA (never distro openocd, never bare upstream).
RUN git clone "${OPENOCD_REPO}" /tmp/openocd \
    && git -C /tmp/openocd checkout --detach "${OPENOCD_SHA}" \
    && git -C /tmp/openocd rev-parse HEAD \
    && cd /tmp/openocd && ./bootstrap && ./configure --prefix=/usr/local \
    && make -j"$(nproc)" && make install && cd / && rm -rf /tmp/openocd \
    && openocd --version | head -2

CMD ["arm-none-eabi-gcc", "--version"]
