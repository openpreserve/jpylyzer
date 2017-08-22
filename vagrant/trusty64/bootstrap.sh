#!/bin/bash

## Installs all dependencies required to build jpylyzer Debian package 
sudo apt-get update
sudo apt-get install -y build-essential debhelper devscripts
sudo apt-get install -y git
sudo apt-get install -y python-pip
sudo apt-get install -y python-dev
sudo pip install --use-mirrors pyinstaller
sudo pip install --use-mirrors six

