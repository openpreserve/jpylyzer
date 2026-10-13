# Build Jpylyzer Windows packages 

function buildAndPackage($pkgname, $pkgversion, $suffix, $pyinstaller) {
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
    # Remove any old instances of this zipped package
    if (Test-Path -Path $zip_name -PathType leaf) {
        Remove-Item -path $zip_name -force
    }
    # Build
    & $pyinstaller --clean -y --distpath $WIN_DIST_DIR $file_spec

    # Zip up the package and clean up
    cd $WIN_DIST_DIR
    Compress-Archive -Path $pkgname -DestinationPath $zip_name
    cd $PSScriptRoot
    if (Test-Path -Path $WIN_DIST_DIR -PathType Container) {
        Remove-Item -path $WIN_DIST_DIR -recurse -force
    }
}

# Python (only used to infer package name and version, so only
# 64 bit is needed)
$python =  "C:\Python314\python.exe"

# 64 and 32 bit Pyinstaller locations
$pyinstaller64 = "C:\Python314\Scripts\pyinstaller.exe"
$pyinstaller32 = "C:\Python314-32\Scripts\pyinstaller.exe"

# Get package name and version
$pkgname = "$(& $python .\setup.py --name)"
$pkgversion = "$(& $python .\setup.py --version)"

# Build 64 and 32 bit packages
buildAndPackage $pkgname $pkgversion "win64" $pyinstaller64
buildAndPackage $pkgname $pkgversion "win32" $pyinstaller32