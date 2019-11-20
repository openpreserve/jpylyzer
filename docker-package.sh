#! /usr/bin/env bash
#
# Build Debian package in a Docker container
#
function getDebianVersionString {
    # Set Debian version string derived from
    # Python version string
    pyVersion=$1

    # Split into major, minor and debug version
    vMajor="$(cut -d'.' -f1 <<<$pyVersion)"
    vMinor="$(cut -d'.' -f2 <<<$pyVersion)"
    vDebug="$(cut -d'.' -f3 <<<$pyVersion)"

    # Length of debug string
    lDebug=${#vDebug}

    # Flag that is True if debug string needs fixing
    fixVDebugFlag=False

    # Locate position of 1st non-numeric character
    # in debug string
    re='^[0-9]+$'
    for i in $(seq 1 ${#vDebug}); do
        echo $i
        char="${vDebug:i-1:1}"
        if [[ $char =~ $re ]] ; then
            splitpos=$i
        else
            fixVDebugFlag=True
            break
        fi
    done

    # Insert tilde in debug string if needed
    if  [ $fixVDebugFlag = "True" ] ; then
        vDebugDebian=${vDebug:0:$splitpos}"~"${vDebug:$splitpos:$lDebug}
    else
        vDebugDebian=$vDebug
    fi

    # Construct Debian version string
    deb_version="$vMajor.$vMinor.$vDebugDebian"
    }

set -e

# Get build platform as 1st argument, and collect project metadata
image="${1:?You MUST provide a docker image name e.g. debian:stretch}"; shift
dist_id=${image%%:*}
codename=${image#*:}
pypi_name="$(./setup.py --name)"
pypi_version="$(./setup.py --version)"
# Generate Debian version string
getDebianVersionString $pypi_version
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
docker run -v "$PWD/dist":/dist --rm $tag cp --force "../opf-jpylyzer_${deb_version}_all.deb" /dist
ls -lh dist/opf?*${pkgname}?*${deb_version//./?}*.*
