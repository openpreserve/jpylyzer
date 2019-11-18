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

# Derive Debian version string from pypi_name
vMajor="$(cut -d'.' -f1 <<<$pypi_version)"
vMinor="$(cut -d'.' -f2 <<<$pypi_version)"
vDebug="$(cut -d'.' -f3 <<<$pypi_version)"
# Length of debug string
lDebug=${#vDebug} 
fixVDebugFlag=False
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

if  [ $fixVDebugFlag = "True" ] ; then 
    vDebugDebian=${vDebug:0:$splitpos}"~"${vDebug:$splitpos:$lDebug}
else
    vDebugDebian=$vDebug
fi
deb_version="$vMajor.$vMinor.$vDebugDebian"

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
