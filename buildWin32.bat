:
:: Build 32 bit Windows jpylyzer binaries from Python script, and pack them in ZIP file
::
:: ZIP file includes license file, PDF User Manual and example files 
::
:: Johan van der Knijff, 25 april 2013
::
:: Dependencies:
:: 
:: - Python 2.7  (PyInstaller doesn't work with Python 3 yet!) 
:: - PyInstaller 2: http://www.pyinstaller.org/
:: - PyWin32 (needed by PyInstaller): http://sourceforge.net/projects/pywin32/files/
:: - a spec file with 
::
@echo off
setlocal

::::::::: CONFIGURATION :::::::::: 

:: Script base name (i.e. script name minus .py extension)
set scriptBaseName=jpylyzer

:: Python
set python=c:\python27\python

:: Path to PyInstaller
set pathPyInstaller=c:\pyinstall\

:: PyInstaller spec file that defines build options
set specFile=jpylyzer_win32.spec

:: Directory where build is created (should be identical to 'name' in 'coll' in spec file!!)
set distDir=.\dist_win32\

:: Executes jpylyzer with -v option and stores output to 
:: env variable 'version'
set vCommand=%python% %scriptBaseName%.py -v
%vCommand% 2> temp.txt
set /p version= < temp.txt
del temp.txt 

::::::::: BUILD :::::::::::::::::: 

:: Build binaries
%python% %pathPyInstaller%\pyinstaller.py %specFile%

:: Generate name for ZIP file
set zipName=%scriptBaseName%_%version%_win32.zip

:: Create ZIP file
%python% zipdir.py %distDir%\jpylyzer %distDir%\%zipName% 

::::::::: CLEANUP ::::::::::::::::: 

:: Delete build directory
rmdir build /S /Q

:: Delete jpylyzer directory in distdir
rmdir %distDir%\jpylyzer /S /Q

::::::::: PARTY TIME! ::::::::::::::::: 

echo /
echo Done! Created %zipName% in directory %distDir%!
echo / 

