# Build Jpylyzer Windows packages 

function Get-Jpylyzer-Version {
    python cli.py --version
}

function buildAndPackage {

}

$SCRIPT_DIR=$PSSCriptRoot

$DIST_DIR=Join-Path -Path $PSSCriptRoot -ChildPath "dist"
$WIN_DIST_DIR=Join-Path -Path $DIST_DIR -ChildPath "windows"

# Get build platform as 1st argument, and collect project metadata
$pypi_name="$(python .\setup.py --name)"
$pypi_version="$(python .\setup.py --version)"
$pkgname=$pypi_name

echo $pkgname
echo $pypi_version

#Get-Jpylyzer-Version
