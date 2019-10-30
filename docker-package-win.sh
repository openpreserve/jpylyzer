#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name}"; shift
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
docker run -v "$PWD/dist":/dist $tag ls -alh ..\
