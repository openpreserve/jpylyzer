#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#
SCRIPT_DIR="$( dirname "$( readlink -f "${BASH_SOURCE[0]}" )")"
DIST_DIR="${SCRIPT_DIR}/dist"
WIN_DIST_DIR="${DIST_DIR}/windows"
set -e

# Get build platform as 1st argument, and collect project metadata
pypi_name="$(./setup.py --name)"
pypi_version="$(./setup.py --version)"
pkgname=$pypi_name

function buildAndPackage(){
    # Installs Python. Arguments:
    # - $1: docker image tag (python3 or python3-32bit)
    # - $2: Windows zip package suffix

    # Set zip package name
    zip_name="${DIST_DIR}/${pkgname}_${pypi_version}_${2}.zip"

    # Remove the windows dist directoruy if it exists
    [ -d ${WIN_DIST_DIR} ] && rm -rf ${WIN_DIST_DIR}
    # Remove any existing zip package
    [ -e ${zip_name} ] && rm ${zip_name}

    # Run the appropriate docker machine (python3-32bit for win32)
    # --rm  Clean up docker container after execution:
    #       https://docs.docker.com/engine/reference/run/#clean-up---rm
    # -v "$(pwd):/src/" Map working directory to container /src:
    #       https://docs.docker.com/engine/reference/run/#volume-shared-filesystems
    docker stop temp-container || true && docker rm temp-container || true
    docker image rm temp-image || true
    docker run -v "$(pwd):/src/" --name temp-container "cdrx/pyinstaller-windows:${1}"
    docker commit temp-container temp-image
    docker run  -v "$(pwd):/src/" --rm temp-image "chown $(id -u):$(id -g) -R /src/dist"
    docker container rm temp-container
    docker image rm temp-image
    # Zip up the package and clean up
    cd "${WIN_DIST_DIR}"
    zip -r ${zip_name} ${pkgname}
    cd ${SCRIPT_DIR}
    [ -d ${WIN_DIST_DIR} ] && rm -rf ${WIN_DIST_DIR}
}

buildAndPackage python3-32bit win32
buildAndPackage python3 win64
