#!/bin/bash

# Bash script to build jpylyzer using PyInstaller

# First check for PyInstaller
command -v pyinstaller >/dev/null 2>&1 || {
    echo >&2 "http://www.pyinstaller.org/ is required to build the Jpylyzer executable.";
    echo >&2 "Please install PyInstaller http://pythonhosted.org/PyInstaller/#installing-pyinstaller.";
    exit 1;
}

# PyInstaller cannot be run as root
originalUserId=$(id -u);
userId=$originalUserId

if [ $originalUserId == 0 ]
then
    uname=$(getent passwd 1000 | cut -d: -f1)
    sudo -u $uname "pyi-makespec --strip --onefile --paths=jpylyzer --specpath=pyi-build ./jpylyzer/jpylyzer.py"
    sudo -u $uname "pyinstaller --strip --clean --paths=jpylyzer --distpath=pyi-build/dist --workpath=pyi-build/build ./pyi-build/jpylyzer.spec"
else
    # So making stripped binaries for debian packaging
    pyi-makespec --strip --onefile --paths=jpylyzer --specpath=pyi-build ./jpylyzer/jpylyzer.py
    pyinstaller --strip --clean --paths=jpylyzer --distpath=pyi-build/dist --workpath=pyi-build/build ./pyi-build/jpylyzer.spec
fi

./pyi-build/dist/jpylyzer --version;
