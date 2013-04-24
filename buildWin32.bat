:
:: Build 32 bit Windows jpylyzer binaries from Python script, and pack them in ZIP file
::
:: ZIP file includes PDF User Manual and test images 
::
:: Johan van der Knijff, 2 March 2011
::
:: Dependencies:
:: 
:: - Python 2.7  (PyInstaller doesn't work with Python 3 yet!) 
:: - PyInstaller: http://www.pyinstaller.org/
:: - PyWin32 (needed by PyInstaller): http://sourceforge.net/projects/pywin32/files/
:: - 7-zip file archiver: http://www.7-zip.org/ 
::
:: To do:  - 64 bit binaries?
::         - Cleanup, get rid off external zip tool dependency (this can probably be all done
::           in PyInstaller)

@echo off
setlocal

::::::::: CONFIGURATION :::::::::: 

:: Script base name (i.e. script name minus .py extension)
set scriptBaseName=jpylyzer

:: Python
set python=c:\python27\python

:: Path to PyInstaller
set pathPyInstaller=c:\pyinstall\

:: Path to 7-zip command-line tool
set zipCommand="C:\Program Files\7-Zip\7z"

:: Executes jpylyzer with -v option and stores output to 
:: env variable 'version'
set vCommand=%python% %scriptBaseName%.py -v
%vCommand% 2> temp.txt
set /p version= < temp.txt
del temp.txt 

::::::::: BUILD :::::::::::::::::: 

:: Make spec file
::%python% %pathPyInstaller%\MakeSpec.py %scriptBaseName%.py

:: Build binaries
::%python% %pathPyInstaller%\build.py %scriptBaseName%.spec

:: Build binaries
%python% %pathPyInstaller%\pyinstaller.py %scriptBaseName%.py


:: Create examples file dir in dist directory
md .\dist\%scriptBaseName%\example_files

:: Copy directory with example files to dist directory
copy /Y .\example_files\* .\dist\%scriptBaseName%\example_files\

:: Create doc directory in dist directory
md .\dist\%scriptBaseName%\doc

:: Copy PDF documentation to doc dir
copy *.pdf .\dist\%scriptBaseName%\doc\

:: Generate name for ZIP file
set zipName=%scriptBaseName%_%version%_win32.zip

:: Create ZIP file
%zipCommand% a -r %zipName% .\dist\jpylyzer\*

:: Delete dist directory that was created by PyInstaller
::rmdir dist /S /Q

md downloads

:: Move ZIP file to downloads directory
move /Y %zipName% .\downloads\

::::::::: CLEANUP ::::::::::::::::: 

:: Delete build directory
rmdir build /S /Q

:: Delete dist directory
rmdir dist /S /Q

:: Rename Win32 directory to dist
::ren win32 dist

:: Delete spec file
::del %scriptBaseName%.spec

echo /
echo Done! Created %zipName% in directory .\downloads\!
echo / 

