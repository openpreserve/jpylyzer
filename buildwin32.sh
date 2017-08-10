# Build Windows binaries from Python script, and pack them in ZIP file

#
# Dependencies:
# - Wine environment with Python, pyInstaller and all jpylyzer dependencies
# - Spec file

# CONFIGURATION 

# Python
# Note that to produce a 32-bit binary we need a 32-bit Python version!
#pythonWine=~/.wine/drive_c/Python27_32/python.exe
pythonWine=~/.wine/dosdevices/c:/Python_32/Scripts/pyinstaller.exe
pyInstallerWine=~/.wine/dosdevices/c:/Python_32/Scripts/pyinstaller.exe

# Script base name (i.e. script name minus .py extension)
scriptBaseName=jpylyzer

# PyInstaller spec file that defines build options
specFile=jpylyzer_win32.spec

# Working directory
workDir=$PWD

# Directory where build is created (should be identical to 'name' in 'coll' in spec file!!)
distDir=./dist/win32/

# Executes jpylyzer with -v option and stores output to 
# env variable 'version'
# Also trim trailing EOL character and replace '.' by '_' 
wine $pythonWine ./$scriptBaseName/$scriptBaseName.py -v 2> temp.txt
version=$(head -n 1 temp.txt | tr -d '\r' |tr '.' '_' )
rm temp.txt

# Build binaries
$pyInstallerWine $specFile --distpath=$distDir

# Generate name for ZIP file
zipName="$scriptBaseName"_"$version"_win32.zip

# Create ZIP file
cd $distDir
zip -r $zipName $scriptBaseName
cd $workDir

# CLEANUP 

# Delete build directory
rm -r ./build
rm -r  $distDir/$scriptBaseName

echo "Done!"

