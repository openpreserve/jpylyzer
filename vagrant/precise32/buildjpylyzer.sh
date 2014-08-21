#!/bin/bash

## Fetch and build jpylyzer
git clone https://github.com/openplanets/jpylyzer.git
cd jpylyzer
dpkg-buildpackage -tc
lintian ../jpylyzer_*.deb
## Clean up
cd ..
rm -rf jpylyzer

