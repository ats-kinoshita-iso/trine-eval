#!/usr/bin/env bash
# Thin wrapper around `docker run` used by the Evaluator when
# `config.sandbox.mode == "docker"`. Isolates a single eval trial inside a
# discardable container so cross-trial state cannot leak between runs.
#
# Usage:
#   scripts/sandbox.sh <verification-command> [args...]
#
# Environment overrides:
#   SANDBOX_IMAGE  — container image to run (default: ubuntu:24.04)
#   SANDBOX_REPO   — host path to mount at /work (default: current working dir)
#   SANDBOX_EXTRA  — extra flags appended to `docker run`
#
# The script intentionally does NOT persist state: --rm discards the container
# on exit, and the mount is read-write only because some eval commands need to
# write artifacts they then read back. Nothing inside the container survives.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <verification-command> [args...]" >&2
  exit 64
fi

image="${SANDBOX_IMAGE:-ubuntu:24.04}"
repo="${SANDBOX_REPO:-$PWD}"
extra="${SANDBOX_EXTRA:-}"

# Literal `docker run --rm -v` is required here (see sprint-06 contract criterion
# 5); keep the invocation inline rather than hiding it behind a variable.
# shellcheck disable=SC2086
exec docker run --rm -v "${repo}:/work" -w /work ${extra} "${image}" "$@"
