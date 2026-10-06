# Build Jpylyzer Windows packages 

function buildAndPackage($pkgname, $pkgversion, $buildtag, $suffix) {
    # Define directory paths
    $DIST_DIR = Join-Path -Path $PSScriptRoot -ChildPath "dist"
    $WIN_DIST_DIR = Join-Path -Path $DIST_DIR -ChildPath "windows"
    # Set zip name and path
    $file_name = $pkgname + "_" + $pkgversion + "_" + $suffix + ".zip"
    $zip_name = Join-Path -Path $DIST_DIR -ChildPath $file_name
    $file_spec = $pkgname + ".spec"
    # Remove the windows dist directory if it exists 
    if (Test-Path -Path $WIN_DIST_DIR -PathType Container) {
        Remove-Item -path $WIN_DIST_DIR -recurse -force
    }
    # Remove any existing zip files
    if (Test-Path -Path $zip_name -PathType leaf) {
        Remove-Item -path $zip_name -force
    }
    # Build
    pyinstaller --clean -y --distpath $WIN_DIST_DIR $file_spec

    # Zip up the package and clean up
    cd $WIN_DIST_DIR
    Compress-Archive -Path $pkgname -DestinationPath $zip_name
    cd $PSScriptRoot
    if (Test-Path -Path $WIN_DIST_DIR -PathType Container) {
        Remove-Item -path $WIN_DIST_DIR -recurse -force
    }
}

# Get package name and version
$pkgname = "$(python .\setup.py --name)"
$pkgversion = "$(python .\setup.py --version)"

buildAndPackage $pkgname $pkgversion "python3" "win64"