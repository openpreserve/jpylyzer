#!/bin/bash

# Build 64 and 32 bit Windows binaries using Wine and WinPython. If the required Wine environment
# (WinPython + PyInstaller) cannot be found it is set up quasi-automatically (the WinPython installer
# needs some manual input)
# Precondition: 64-bit version of Wine is already installed.
export DISPLAY=:0.0
# WinPython download URLS
python3Major=3
python3Minor=6
winPython3build="5.0"
sfWpRoot="https://sourceforge.net/projects/winpython/files/"
sfWpPost="Zero.exe/download"
winPyName="WinPython"

# Script base name (i.e. script name minus .py extension)
scriptBaseName=jpylyzer

# Wine debug variable (suppresses garbage debugging messages)
WineDebug="-msvcrt,-ntdll,-toolhelp"

function winPyDownloadUrl() {
  # - $1: bitness (32 or 64)
  # - $2: Python major version
  # - $3: Python minor version
  # - $4: WinPython build number
  if [ $2 == "2" ]; then
    echo "${sfWpRoot}${winPyName}_${2}.${3}/${2}.${3}.${4}/${winPyName}-${1}bit-${2}.${3}.${4}${sfWpPost}"
  else
    echo "${sfWpRoot}${winPyName}_${2}.${3}/${2}.${3}.${4}/${winPyName}${1}-${2}.${3}.${4}${sfWpPost}"
  fi
}

function winePythonHome() {
  # - $1: bitness (32 or 64)
  # - $2: Python major version
  # - $3: Python minor version
  echo "$(winePrefix $1)/drive_c/Python${2}${3}_${1}"
}

function winePrefix() {
  # - $1: bitness (32 or 64)
  echo "${HOME}/.$(winArch $1)"
}

function winArch() {
  # - $1: bitness (32 or 64)
  echo "win${1}"
}

installPython(){
    # Installs Python. Arguments:
    # - $1: bitness (32 or 64)
    # - $2: Python major version
    # - $3: Python minor version
    # - $4: WinPython build number
    downloadUrl=$(winPyDownloadUrl $1 $2 $3 $4)
    winePythonHome=$(winePythonHome $1 $2 $3)
    echo "Downloading installer from ${downloadUrl}"
    wget $downloadUrl -q -O pyTemp.exe
    echo ""
    echo "Installing Python."
    echo ""

    7z x -o"${winePythonHome}" pyTemp.exe

    echo "Removing installer"
    rm pyTemp.exe
}

installPyInstaller(){
    # Installs pyInstaller if it is not installed already. Argument:
    # - $1: Python path
    # - $2: bitness
    echo "Upgrading pip for ${1}"
    WINEDEBUG=$WineDebug WINEPREFIX=$(winePrefix $2) wine $1 -m pip install --upgrade pip
    echo "Checking for pyinstaller ${1}"
    WINEDEBUG=$WineDebug WINEPREFIX=$(winePrefix $2) wine $1 -m pip show pyinstaller

    if [ $? -eq 0 ]; then
        echo "Pyinstaller already installed"
    else
        echo "Installing pyinstaller"
        WINEDEBUG=$WineDebug WINEPREFIX=$(winePrefix $2) wine $1 -m pip install pyinstaller
    fi
}

buildBinaries(){
    # Builds Windows binaries.

    # Read arguments:
    bitness=$1
    pyRoot=$2
    pyInstallerWine="${pyRoot}/Scripts/pyinstaller.exe"
    pythonWine=$3
    specFile=$4
    pythonMajor=$5

    # Working directory
    workDir=$PWD

    # Directory where build is created (should be identical to 'name' in 'coll' in spec file!!)
    distDir="${workDir}/dist/win${bitness}/"

    # Executes jpylyzer with -v option and stores output to
    # env variable 'version'
    # Also trim trailing EOL character and replace '.' by '_'
    if [ $pythonMajor == "2" ]; then
      WINEDEBUG=$WineDebug WINEPREFIX=$(winePrefix $bitness) wine $pythonWine -m $scriptBaseName -v 2> temp.txt
      version=$(head -n 1 temp.txt | tr -d '\r')
      rm temp.txt
    else
      version="$(WINEDEBUG="${WineDebug}" WINEPREFIX="$(winePrefix "${bitness}")" wine "${pythonWine}" -m "${scriptBaseName}" -v)"
    fi

    version="$(echo -e "${version}" | tr -d '[:space:]')"
    echo "Building binaries ${version}"
    WINEDEBUG=$WineDebug WINEPREFIX=$(winePrefix $bitness) wine $pyInstallerWine $specFile --distpath=$distDir

    # Generate name for ZIP file
    zipName="${scriptBaseName}_${version}_win${bitness}.zip"
    echo "Zip name is $zipName"
    echo ""
    echo "Creating ZIP file ${zipName} from ${scriptBaseName}"
    echo ""
    cd $distDir || exit
    zip -r $zipName $scriptBaseName
    cd $workDir || exit

    echo "Deleting build directory"
    rm -r "${workDir}/build"
    rm -r "${distDir:?}/${scriptBaseName}"
}


installAndBuild(){
    # Installs Python and builds the packages. Arguments:
    # - $1: bitness (32 or 64)
    # - $2: Python major version
    # - $3: Python minor version
    # - $4: WinPython build number
    bitness=$1
    pythonMajor=$2
    pythonMinor=$3
    winPythonBuild=$4
    winPyHome=$(winePythonHome $bitness $pythonMajor $pythonMinor)
    echo "${bitness} bit Python"
    if [ -d "${winPyHome}" ]; then
        echo "Python (${bitness} bit) already installed"
    else
        echo "Python (${bitness} bit) not yet installed, installing now"
        echo ""
        installPython $bitness $pythonMajor $pythonMinor $winPythonBuild
    fi

    # Get path to Python root
    pyRoot=$(ls -d $winPyHome/python-*)

    # Python interpreter
    python="${pyRoot}/python.exe"

    # Install PyInstaller (if not installed already)
    installPyInstaller $python $bitness

    echo "Building Python${pythonMajor} binaries, ${bitness} bit"
    buildBinaries $bitness $pyRoot $python "jpylyzer_win${bitness}.spec" $pythonMajor
}

# Create Win32 architecture
WINEARCH=$(winArch 32) WINEPREFIX=$(winePrefix 32) winecfg
WINEARCH=$(winArch 64) WINEPREFIX=$(winePrefix 64) winecfg
installAndBuild 64 $python3Major $python3Minor $winPython3build
installAndBuild 32 $python3Major $python3Minor $winPython3build
