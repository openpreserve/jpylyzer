#!/usr/bin/env python
"""Setup script for jpylyzer"""
import codecs
import os
import re
from setuptools import setup, find_packages

def read(*parts):
    """Read file and return contents"""
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()

def find_version(*file_paths):
    """Find and return version number"""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

INSTALL_REQUIRES = ['setuptools', 'six']
PYTHON_REQUIRES = '>=2.7, !=3.0.*, !=3.1.*, <4'

TEST_DEPS = [
    'pre-commit',
    'pytest',
    'pylint',
    'pytest-coverage'
]
EXTRAS = {
    'testing': TEST_DEPS,
}

README = open('README.md', 'r')
README_TEXT = README.read()
README.close()

setup(name='jpylyzer',
      packages=find_packages(),
      version=find_version('jpylyzer', 'jpylyzer.py'),
      license='LGPL',
      install_requires=INSTALL_REQUIRES,
      tests_requires=TEST_DEPS,
      extras_require=EXTRAS,
      python_requires=PYTHON_REQUIRES,
      platforms=['POSIX', 'Windows'],
      description='JP2 (JPEG 2000 Part 1) image validator and properties extractor',
      long_description=README_TEXT,
      long_description_content_type='text/markdown',
      author='Johan van der Knijff',
      author_email='johan.vanderknijff@kb.nl',
      maintainer='Johan van der Knijff',
      maintainer_email='johan.vanderknijff@kb.nl',
      url='http://jpylyzer.openpreservation.org/',
      download_url='https://github.com/openpreserve/jpylyzer/archive/' \
        + find_version('jpylyzer', 'jpylyzer.py') + '.tar.gz',
      package_data={'jpylyzer': ['*.*']},
      entry_points={'console_scripts': [
          'jpylyzer = jpylyzer.jpylyzer:main',
      ]},
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ]
     )
