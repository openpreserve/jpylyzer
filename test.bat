:
:: Build 32 bit Windows jpylyzer binaries from Python script, and pack them in ZIP file
::
:: ZIP file includes PDF User Manual and test images 
::
:: Johan van der Knijff, 1 March 2011
::
:: Dependencies:
:: 
:: - Python 2.7  (PyInstaller doesn't work with Python 3 yet!) 
:: - PyInstaller: http://www.pyinstaller.org/
:: - PyWin32 (needed by PyInstaller): http://sourceforge.net/projects/pywin32/files/
:: - 7-zip file archiver: http://www.7-zip.org/ 
::
:: To do: 64 bit binaries?

::::::::: CONFIGURATION :::::::::: 

:: Script base name (i.e. script name minus .py extension)
set scriptBaseName=jpylyzer

:: Python
set python=c:\python27\python

:: Path to PyInstaller
set pathPyInstaller=c:\pyinstall\

:: Path to 7-zip command-line tool
set zipCommand="C:\Program Files\7-Zip\7z"


::::::::: GET VERSION INFO :::::::::: 

:: Executes jpylyzer with -v option and stores output to 
:: env variable 'version'
set vCommand=%python% %scriptBaseName%.py -v

%vCommand% 2> temp.txt
set /p version= < temp.txt
del temp.txt

::for /f "tokens=*" %%i in ('%vCommand%') do set version=%%i 

::::::::: BUILD :::::::::::::::::: 

:: Generate name for ZIP file
set zipName=%scriptBaseName%_%version%_win32.zip

echo version  is %version%
echo %zipName%
