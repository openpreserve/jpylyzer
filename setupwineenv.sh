#!/bin/bash

# Set up Wine environment for Windows builds. Precondition: 64-bit version of Wine is already installed. 

# WinPython download URLS
downloadURL64bit=https://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.13.1/WinPython-64bit-2.7.13.1Zero.exe/download
downloadURL32bit=https://sourceforge.net/projects/winpython/files/WinPython_2.7/2.7.13.1/WinPython-32bit-2.7.13.1Zero.exe/download

echo "64 bit Python"

if [ -d $HOME"/.wine/drive_c/Python27_64" ]; then  
    echo "Python (64 bit) already installed"
else
    echo "Python (64 bit) not yet installed, installing now"
    echo ""
    
    echo "Downloading installer"
    wget $downloadURL64bit -O py64.exe

    echo "Installing Python. This requires some user input"
    echo ""
    echo "Follow installer instructions. For Destination Folder replace default path with C:\Python27_64"
    echo ""

    wine py64.exe

    echo "Removing installer"
    rm py64.exe
fi

# Get path to Python root
pyRoot64=$(ls -d ~/.wine/drive_c/Python27_64/python-*)

# Python interpreter
python64=$pyRoot64"/python.exe" 

echo "Checking for pyinstaller" 
wine $python64 -c "import pyinstaller"

if [ $? -eq 0 ]; then
    echo "Pyinstaller already installed"
else
    echo "Installing pyinstaller"
    wine $python64 -m pip install pyinstaller
fi

echo "32 bit Python"

if [ -d $HOME"/.wine/drive_c/Python27_32" ]; then  
    echo "Python (32 bit) already installed"
else
    echo "Python (32 bit) not yet installed, installing now"
    echo ""
    
    echo "Downloading installer"
    wget $downloadURL32bit -O py32.exe

    echo "Installing Python. This requires some user input"
    echo ""
    echo "Follow installer instructions. For Destination Folder replace default path with C:\Python27_32"
    echo ""

    wine py32.exe

    echo "Removing installer"
    rm py32.exe
fi

# Get path to Python root
pyRoot32=$(ls -d ~/.wine/drive_c/Python27_32/python-*)

# Python interpreter
python32=$pyRoot32"/python.exe" 

echo "Checking for pyinstaller" 
wine $python32 -c "import pyinstaller"

if [ $? -eq 0 ]; then
    echo "Pyinstaller already installed"
else
    echo "Installing pyinstaller"
    wine $python32 -m pip install pyinstaller
fi

echo "Done!"
echo ""
echo "Python root (64 bit): "$pyRoot64
echo "Python (64 bit): "$python64
echo "Python root (32 bit): "$pyRoot32
echo "Python (32 bit): "$python32
echo ""


