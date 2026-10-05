:: Build Windows jpylyzer binaries
::
@echo off
setlocal

:: Script base name (i.e. script name minus .py extension)
set scriptBaseName=jpylyzer

:: Build
pyi-makespec --paths=%scriptBaseName% --name=%scriptBaseName% --specpath=pyi-build ./cli.py
pyinstaller --clean --distpath=pyi-build/dist --workpath=pyi-build/build ./pyi-build/%scriptBaseName%.spec
