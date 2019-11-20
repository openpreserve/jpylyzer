#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name e.g. debian:stretch}"; shift
dist_id=${image%%:*}
codename=${image#*:}
pypi_name="$(./setup.py --name)"
pypi_version="$(./setup.py --version)"
pkgname=$pypi_name

tag="${pypi_name}-win"
docker build --tag $tag \
    --build-arg "DIST_ID=$dist_id" \
    --build-arg "CODENAME=$codename" \
    --build-arg "PKGNAME=$pkgname" \
    --build-arg "VERSION=$pypi_version" \
    -f Dockerfile-Wine.build \
    "$@" .
    mkdir -p dist
docker run -v "$PWD/dist":/dist --rm $tag cp --force --recursive dist/win32 dist/win64 /dist
