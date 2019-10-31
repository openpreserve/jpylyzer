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
deb_version=2.0.0~rc1
pkgname=$pypi_name
tag=$pypi_name-$dist_id-$codename
# Build in Docker container, save results, and show package info
rm -f dist/${pkgname}?*${pypi_version//./?}*${codename}*.*
docker build --tag $tag \
    --build-arg "DIST_ID=$dist_id" \
    --build-arg "CODENAME=$codename" \
    --build-arg "PKGNAME=$pkgname" \
    --build-arg "VERSION=$pypi_version" \
    -f Dockerfile.build \
    "$@" .
mkdir -p dist
docker run -v "$PWD/dist":/dist --rm $tag cp --force "../python-jpylyzer-doc_${deb_version}_all.deb" "../python-jpylyzer_${deb_version}_all.deb" "../python3-jpylyzer_${deb_version}_all.deb" /dist
ls -lh dist/python?*${pkgname}?*${deb_version//./?}*.*
