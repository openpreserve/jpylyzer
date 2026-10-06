# Build Jpylyzer Windows packages 

function buildAndPackage($DIST_DIR, $pkgname, $pkgversion, $buildtag, $suffix) {
    # Set zip package name
    $file_name = $pkgname + "_" + $pkgversion + "_" + $suffix + ".zip"
    $zip_name = Join-Path -Path $DIST_DIR -ChildPath $file_name
    echo $zip_name
}

$SCRIPT_DIR = $PSSCriptRoot
$DIST_DIR = Join-Path -Path $PSSCriptRoot -ChildPath "dist"
$WIN_DIST_DIR = Join-Path -Path $DIST_DIR -ChildPath "windows"

# Get package name and version
$pkgname = "$(python .\setup.py --name)"
$pkgversion = "$(python .\setup.py --version)"

buildAndPackage $DIST_DIR $pkgname $pkgversion "python3" "win64"