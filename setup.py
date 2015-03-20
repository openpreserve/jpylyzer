#!/usr/bin/env python

from distutils.core import setup

# TO DO: figure out how to import version number automatically from code!

readme = open('README.txt', 'r')
README_TEXT = readme.read()
readme.close()

setup(name='jpylyzer',
      packages=['jpylyzer'],
      version='1.14.0',
      license='LGPL',
      platforms=['POSIX', 'Windows'],
      description='JP2 (JPEG 2000 Part 1) image validator and properties extractor',
      long_description=README_TEXT,
      author='Johan van der Knijff',
      author_email='johan.vanderknijff@kb.nl',
      maintainer='Johan van der Knijff',
      maintainer_email='johan.vanderknijff@kb.nl',
      url='http://jpylyzer.openpreservation.org/'
      )
