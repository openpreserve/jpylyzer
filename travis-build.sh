#!/bin/sh 
python Makespec.py --onefile jpylyzer.py
python pyinstaller.py jpylyzer.spec
