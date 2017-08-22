#!/bin/bash

# Bash script to build jpylyzer using PyInstaller

# Script base name (i.e. script name minus .py extension)
scriptBaseName=jpylyzer

# First check for PyInstaller
command -v pyinstaller >/dev/null 2>&1 || {
    echo >&2 "PyInstaller is required to build the executable.";
    echo >&2 "Please install PyInstaller with:";
    echo >&2 "  (sudo) pip install pyinstaller"
    exit 1;
}

# PyInstaller cannot be run as root
originalUserId=$(id -u);
userId=$originalUserId

if [ $originalUserId == 0 ]
then
    uname=$(getent passwd 1000 | cut -d: -f1)
    sudo -u $uname "pyi-makespec --strip --onefile --paths=$scriptBaseName --name=$scriptBaseName --specpath=pyi-build ./cli.py"
    sudo -u $uname "pyinstaller --strip --clean --paths=$scriptBaseName --distpath=pyi-build/dist --workpath=pyi-build/build ./pyi-build/$scriptBaseName.spec"
else
    # So making stripped binaries for debian packaging
    pyi-makespec --strip --onefile --paths=$scriptBaseName --name=$scriptBaseName --specpath=pyi-build ./cli.py
    pyinstaller --strip --clean --paths=$scriptBaseName --distpath=pyi-build/dist --workpath=pyi-build/build ./pyi-build/$scriptBaseName.spec
fi

./pyi-build/dist/$scriptBaseName --version;
