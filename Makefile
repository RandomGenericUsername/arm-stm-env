# arm-stm-env — fresh-clone rebuild with make.
#
# Fresh machine path:
#   1. `make sync`        (uv-managed Python env)
#   2. `make test`        (engine suite, no Docker needed)
#   3. `make images`      (builds cpp+rust images; needs Docker, slow first time)
#   4. `make smoke`       (runs version probes inside both images)
#   5. `make push`        (publishes to $REGISTRY; needs `docker login`)
#
# Knobs: PLATFORM (default linux/amd64 — toolchain URLs are x86_64;
#          native arm64 images need arch-aware Dockerfiles, not yet supported),
#        REGISTRY (default ghcr.io/arm-stm-env), TAG_CPP, TAG_RUST.

PLATFORM   ?= linux/amd64
REGISTRY   ?= ghcr.io/arm-stm-env
TAG_CPP    ?= 15.3.rel2
TAG_RUST   ?= 1.99.0
IMG_CPP    := $(REGISTRY)/lang-cpp:$(TAG_CPP)
IMG_RUST   := $(REGISTRY)/lang-rust:$(TAG_RUST)

.PHONY: help sync test images image-cpp image-rust smoke push push-cpp push-rust digests clean

help:
	@echo "sync         Install Python env (uv sync --frozen)"
	@echo "test         Run engine test suite"
	@echo "images       Build cpp + rust images (needs Docker)"
	@echo "image-cpp    Build cpp image only"
	@echo "image-rust   Build rust image only"
	@echo "smoke        Version probes inside both images"
	@echo "digests      Print image digests for README recording"
	@echo "push         Push both images to \$$(REGISTRY) (needs docker login)"
	@echo "clean        Remove local arm-stm-env images"

sync:
	uv sync --frozen

test:
	uv run python -m pytest engine/ -q

images: image-cpp image-rust

image-cpp:
	docker build --platform $(PLATFORM) -t $(IMG_CPP) -f images/cpp.Dockerfile images/

image-rust:
	docker build --platform $(PLATFORM) -t $(IMG_RUST) -f images/rust.Dockerfile images/

smoke:
	docker run --rm --platform $(PLATFORM) $(IMG_CPP) arm-none-eabi-gcc --version
	docker run --rm --platform $(PLATFORM) $(IMG_CPP) openocd --version
	docker run --rm --platform $(PLATFORM) $(IMG_RUST) rustc --version
	docker run --rm --platform $(PLATFORM) $(IMG_RUST) probe-rs --version
	docker run --rm --platform $(PLATFORM) $(IMG_RUST) rustup target list --installed

digests:
	docker inspect $(IMG_CPP) --format='cpp: {{.RepoDigests}}'
	docker inspect $(IMG_RUST) --format='{{.RepoDigests}}'

push: push-cpp push-rust

push-cpp:
	docker push $(IMG_CPP)

push-rust:
	docker push $(IMG_RUST)

clean:
	docker rmi -f $(IMG_CPP) $(IMG_RUST) 2>/dev/null || true
