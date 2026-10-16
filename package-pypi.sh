#!/bin/bash

# This script creates a distribution and uploads it to PyPi
# 
# Requirements:
#
# build (python3 -m pip install --upgrade build)
# twine (python3 -m pip install --upgrade twine)
#
# Repository: this is usually pypi; for testing use testpypi
# The corresponding repository URLS are defined in config file ~/.pypirc
#
#repository=testpypi
repository=pypi

# Working directory
workDir=$PWD

# Dist directory
distDir=$workDir"/dist/"

# Clear contents of dist dir if it exists
if [ -d "$distDir" ]; then
    rm -r "$distDir"
fi

# Build
python3 -m build

# Upload package if build was successful; if not show error message
if [ $? -eq 0 ]; then
    python3 -m twine upload --repository $repository dist/*
else
    echo "Build not successful, quitting now ..."
fi


