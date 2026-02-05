#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
projdir="$(dirname "$PWD")"
git submodule update --init
./docker-pip-compile/docker-pip-compile.sh "$projdir"
docker build -t nikolausers:latest -f "$projdir/docker/Dockerfile" "$projdir"
