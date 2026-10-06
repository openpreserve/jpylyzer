# Build Jpylyzer Windows packages 

function buildAndPackage($DIST_DIR, $WIN_DIST_DIR, $pkgname, $pkgversion, $buildtag, $suffix) {
    # Set zip package name
    $file_name = $pkgname + "_" + $pkgversion + "_" + $suffix + ".zip"
    $zip_name = Join-Path -Path $DIST_DIR -ChildPath $file_name
    # Remove the windows dist directory if it exists 
    if (Test-Path -Path $WIN_DIST_DIR -PathType Container) {
        Remove-Item -path $WIN_DIST_DIR -recurse -force
    }
    # Remove any existing zip package
    if (Test-Path -Path $zip_name -PathType leaf) {
        Remove-Item -path $zip_name -force
    }
}

$SCRIPT_DIR = $PSSCriptRoot
$DIST_DIR = Join-Path -Path $PSSCriptRoot -ChildPath "dist"
$WIN_DIST_DIR = Join-Path -Path $DIST_DIR -ChildPath "windows"

# Get package name and version
$pkgname = "$(python .\setup.py --name)"
$pkgversion = "$(python .\setup.py --version)"

buildAndPackage $DIST_DIR $WIN_DIST_DIR $pkgname $pkgversion "python3" "win64"