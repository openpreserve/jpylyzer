#!/bin/bash

# This script creates a wheel distribution and uploads it to PyPi
# 
# Requirements:
#
# twine https://pypi.python.org/pypi/twine/1.9.1 (pip install twine)
# wheel https://pypi.python.org/pypi/wheel (pip install wheel)

# Repository: this is usually pypi; for testing use testpypi
# The corresponding repository URLS are defined in config file ~/.pypirc
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

# Create wheel
python setup.py sdist bdist_wheel --universal

# Upload package if wheel build was successful; if not show error message
if [ $? -eq 0 ]; then
    twine upload --repository $repository  dist/*
else
    echo "Wheel build not successful quitting now ..."
fi


