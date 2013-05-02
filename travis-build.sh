#!/bin/sh 
python Makespec.py --onefile ./jpylyzer/jpylyzer.py
python pyinstaller.py jpylyzer.spec
