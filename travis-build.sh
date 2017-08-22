#!/bin/sh 
pyi-makespec --onefile --name=jpylyzer ./cli.py
pyinstaller jpylyzer.spec

