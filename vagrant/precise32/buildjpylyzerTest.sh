#!/bin/bash

## Fetch and build jpylyzer
git clone -b recnstna https://github.com/openpreserve/jpylyzer.git
cd jpylyzer
dpkg-buildpackage -tc
lintian ../jpylyzer_*.deb
## Clean up
cd ..
rm -rf jpylyzer

