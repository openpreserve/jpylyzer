#!/usr/bin/env python

from distutils.core import setup

readme = open('README.txt', 'r')
README_TEXT = readme.read()
readme.close()


setup(name = 'jpylyzer',
    version = '1.9.2',
    description = 'JP2 (JPEG 2000 Part 1) image validator and properties extractor',
    long_description = README_TEXT,
    author = 'Johan van der Knijff',
    author_email = 'johan.vanderknijff@kb.nl',
    maintainer = 'Johan van der Knijff',
    maintainer_email = 'johan.vanderknijff@kb.nl',
    url = 'https://github.com/openplanets/jpylyzer',
    packages = ['jpylyzer'],
    license = 'GNU Lesser General Public License'
    )
