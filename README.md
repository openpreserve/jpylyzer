# jpylyzer

## About
*Jpylyzer* is a JP2 [(JPEG 2000 Part 1)][2] image validator and properties extractor. Its development was partially supported by the [SCAPE][4] Project. The SCAPE project is co-funded by the European Union under FP7 ICT-2009.4.1 (Grant Agreement number 270137).

## Jpylyzer homepage

Please visit the jpylyzer homepage for links to the most recent package downloads (Debian packages and Windows binaries), and a User Manual which documents all aspects of the software:

<http://jpylyzer.openpreservation.org/>


## Cd Status

- [![Build Status](https://travis-ci.org/openpreserve/jpylyzer.svg?branch=master)](https://travis-ci.org/openpreserve/jpylyzer "Jpylyzer Travis-CI integration build") Travis-CI

- [![Build Status](http://jenkins.opf-labs.org/buildStatus/icon?job=jpylyser)](http://jenkins.opf-labs.org/job/jpylyser/) OPF Jenkins

## Command line use

### Usage

    usage: jpylyzer [-h] [--verbose] [--recurse] [--wrapper] [--nullxml]
                       [--nopretty] [--version] jp2In [jp2In ...]

### Positional arguments

`jp2In` : input JP2 image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux.

### Optional arguments

`-h, --help` : show this help message and exit;

`-v, --version` : show program's version number and exit;

`--verbose` : report test results in verbose format;

`--recurse, -r` : when analysing a directory, recurse into subdirectories (implies `--wrapper`)

`--wrapper, -w` : wrap the output for individual image(s) in 'results' XML element.

`--nullxml` : extract null-terminated XML content from XML and UUID boxes (doesn't affect validation)

`--nopretty` : suppress pretty-printing of XML output

## Output 

Output is directed to the standard output device (*stdout*).

### Example

`jpylyzer.py rubbish.jp2 > rubbish.xml`

In the above example, output is redirected to the file 'rubbish.xml'.


### Outline of output elements

1. *toolInfo*: tool name (jpylyzer) + version.
2. *fileInfo*: name, path, size and last modified time/date of input file.
3. *isValidJP2*: *True* / *False* flag indicating whether file is valid JP2.
4. *tests*: tree of test outcomes, expressed as *True* / *False* flags.
   A file is considered valid JP2 only if all tests return *True*. Tree follows JP2 box structure. By default only tests that returned *False* are reported, which results in an empty *tests*  element for files that are valid JP2. Use the  `--verbose` flag to get *all* test results.
5. *properties*: tree of image properties. Follows JP2 box structure. Naming of properties follows [ISO/IEC 15444-1 Annex I][2] (JP2 file format syntax) and [Annex A][3] (Codestream syntax).

## Using jpylyzer as a Python module

In order to use *jpylyzer* in your own Python programs, first install it
with *pip*. Then import *jpylyzer* into your code by adding:

```python
from jpylyzer import jpylyzer
```

Subsequently you can call any function that is defined in *jpylyzer.py*.
In practice you will most likely only need the *checkOneFile* function. 
The following minimal script shows how this works:

```python
from jpylyzer import jpylyzer
# Define JP2
myFile = "/home/johan/jpylyzer-test-files/aware.jp2"

# Analyse with jpylyzer, result to Element object
myResult = jpylyzer.checkOneFile(myFile)

# Return image height value
imageHeight = myResult.findtext('./properties/jp2HeaderBox/imageHeaderBox/height')
print(imageHeight)
```

## Debian packages build process

The [Vagrant directory](vagrant) of this repo contains instructions on how to build Debian packages using [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/). A Vagrantfile and provisioning scripts are included for a number of target platforms, which should make the process of building the packages fairly easy.

## Steps in preparing a jpylyzer release

[See instructions here](./howto-prepare-release.md)

[1]: http://jpylyzer.openpreservation.org//jpylyzerUserManual.html
[2]: http://www.jpeg.org/public/15444-1annexi.pdf
[3]: http://www.itu.int/rec/T-REC-T.800/en
[4]: http://www.scape-project.eu/
[5]: https://bintray.com/openplanets/opf-windows/jpylyzer_win32/
[6]: https://bintray.com/openplanets/opf-debian/jpylyzer_i386/
[7]: https://bintray.com/openplanets/opf-debian/jpylyzer_amd64/
