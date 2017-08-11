#!/bin/bash

scriptBaseName=jpylyzer
bitness=64
workDir=$PWD
#pythonWine=/home/johan/.wine/drive_c/Python27_64/python-2.7.13.amd64/python.exe
pythonWine=/home/johan/.wine/drive_c/Python27_32/python-2.7.13/python.exe

wine $pythonWine $workDir"/$scriptBaseName/$scriptBaseName.py" -v 2> temp.txt
version=$(head -n 1 temp.txt | tr -d '\r' |tr '.' '_' )
echo $version

zipName=$scriptBaseName"_"$version"_win"$bitness".zip"
echo $zipName
