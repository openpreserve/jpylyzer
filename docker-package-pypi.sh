#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#

set -e

# Get build platform as 1st argument, and collect project metadata
pypi_name="$(./setup.py --name)"

# Build in Docker container, save results, and show package info
docker run -v "$PWD":/src -v "$HOME":/pypirc --entrypoint "/src/package-pypi.sh" --rm python:3.6-stretch 
