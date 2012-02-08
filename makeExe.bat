
@echo off

:: USAGE: makeExe pythonScriptBaseName (without .py)


:: Set base name of script to compile
set BaseName=%1

:: Set personal Path to the Apps:
set PythonEXE=C:\Python27\python.exe

:: Display syntax if base name is not given
if not exist %BaseName%.py      call :FileNotFound %BaseName%.py
if not exist %PythonEXE%        call :FileNotFound %PythonEXE%

::Write the Py2EXE-Setup File
call :MakeSetupFile >"%BaseName%_EXESetup.py"


::Compile the Python-Script
%PythonEXE% "%BaseName%_EXESetup.py" py2exe
::errorlevel%"=="0" (
::         echo Py2EXE Error!
::         goto:eof
::)


:: Delete the Py2EXE-Setup File
del "%BaseName%_EXESetup.py"

:: Copy the Py2EXE Results to the SubDirectory and Clean Py2EXE-Results
rd build /s /q
xcopy dist\*.* "distWin32\" /d /y
rd dist /s /q

echo Done: "distWin32\"
echo.
goto:eof


:MakeSetupFile
         echo.
         echo from distutils.core import setup
         echo import py2exe
         echo.
     echo setup (console=["%BaseName%.py"],
     echo zipfile="%BaseName%Lib.zip",
         echo    options = {"py2exe": {"packages": ["encodings"]}})
         echo.
goto:eof


:FileNotFound
         echo.
         echo Error, File not found:
         echo [%1]
         echo.
         echo Check Path in %~nx0???
         echo.
goto:eof