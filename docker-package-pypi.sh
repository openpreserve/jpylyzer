#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# Build in Docker container, save results, and show package info
docker run -v "$PWD":/src -v "$HOME":/pypirc --entrypoint "/src/package-pypi.sh" --rm python:3.6-stretch
