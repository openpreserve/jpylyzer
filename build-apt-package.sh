#!/bin/sh 

# Bash script to build jpylyzer using PyInstaller

# First check for PyInstaller
command -v pyinstaller >/dev/null 2>&1 || {
    echo >&2 "http://www.pyinstaller.org/ is required to build the Jpylyzer executable.";
    echo >&2 "Please install PyInstaller http://pythonhosted.org/PyInstaller/#installing-pyinstaller.";
    exit 1; 
}

# So making stripped binaries for debian packaging
pyi-makespec --strip --onefile --specpath=pyi-build ./jpylyzer/jpylyzer.py
pyinstaller --strip --clean --distpath=pyi-build/dist --workpath=pyi-build/build ./pyi-build/jpylyzer.spec

