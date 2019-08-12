# jpylyzer

## About
*Jpylyzer* is a JP2 [(JPEG 2000 Part 1)][2] image validator and properties extractor. Its development was partially supported by the [SCAPE][4] Project. The SCAPE project is co-funded by the European Union under FP7 ICT-2009.4.1 (Grant Agreement number 270137).

## Jpylyzer homepage

Please visit the jpylyzer homepage for links to the most recent package downloads (Debian packages and Windows binaries), and a User Manual which documents all aspects of the software:

<http://jpylyzer.openpreservation.org/>


## Cd Status

- [![Build Status](https://travis-ci.org/openpreserve/jpylyzer.svg?branch=master)](https://travis-ci.org/openpreserve/jpylyzer "Jpylyzer Travis-CI integration build") Travis-CI

- [![Build Status](http://jenkins.opf-labs.org/buildStatus/icon?job=jpylyser)](http://jenkins.opf-labs.org/job/jpylyser/) OPF Jenkins

<!-- Start of text to be copied to usage.md of jpylyzer website -->

## Using jpylyzer from the command line

Calling *jpylyzer* in a command window without any arguments results in the following helper message:

    usage: jpylyzer [-h] [--format FMT] [--legacyout] [--mix {1,2}] [--nopretty]
              [--nullxml] [--recurse] [--verbose] [--version] [--wrapper]
              jp2In [jp2In ...]

### Positional arguments

|Argument|Description|
|:--|:--|
|`jp2In`|input JP2 image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux|

### Optional arguments

|Argument|Description|
|:--|:--|
|`[-h, --help]`|show help message and exit|
|`[--format FMT]`|validation format; allowed values are `jp2` (used by default) and `j2c` (which activates raw codestream validation)|
|`[--mix {1,2}]`|report additional output in NISO MIX format (version 1.0 or 2.0)|
|`[--legacyout]`|report output in jpylyzer 1.x format (provided for backward compatibility only)|
|`[--nopretty]`|suppress pretty-printing of XML output|
|`[--nullxml]`|extract null-terminated XML content from XML and UUID boxes(doesn't affect validation)|
|`[--recurse, -r]`|when analysing a directory, recurse into subdirectories (implies `--wrapper` if `--legacyout` is used)|
|`[--verbose]`|report test results in verbose format|
|`[-v, --version]`|show program's version number and exit|
|`[--wrapper, -w]`|wrap output for individual image(s) in 'results' XML element (deprecated from jpylyzer 2.x onward, only takes effect if `--legacyout` is used)|

## Output

Output is directed to the standard output device (*stdout*).

### Example

`jpylyzer rubbish.jp2 > rubbish.xml`

In the above example, output is redirected to the file &#8216;rubbish.xml&#8217;. By default *jpylyzer*&#8217;s XML is pretty-printed, so you should be able to view the file using your favourite text editor. Alternatively use a dedicated XML editor, or open the file in your web browser.

## Output format

The output file contains the following top-level elements:

1. One *toolInfo* element, which contains information about *jpylyzer* (its name and version number)

2. One or more *file* elements, each of which contain information about about the analysed files


In turn, each *file* element contains the following sub-elements:


1. *fileInfo*: general information about the analysed file

2. *statusInfo*: information about the status of *jpylyzer*'s validation attempt

3. *isValid*: outcome of the validation

4. *tests*: outcome of the individual tests that are part of the
validation process (organised by box)

5. *properties*: image properties (organised by box)

6. *propertiesExtension*: wrapper element for NISO *MIX* output (only if the `--mix` option is used)

## Using jpylyzer as a Python module

Instead of using *jpylyzer* from the command-line, you can also import
it as a module in your own Python programs. To do so, install jpylyzer
with *pip*. Then import *jpylyzer* into your code by adding:

```python
from jpylyzer import jpylyzer
```
Subsequently you can call any function that is defined in *jpylyzer.py*.
In practice you will most likely only need the *checkOneFile* function. 
The following minimal script shows how this works:

```python
#! /usr/bin/env python

from jpylyzer import jpylyzer

# Define JP2
myFile = "/home/johan/jpylyzer-test-files/aware.jp2"

# Analyse with jpylyzer, result to Element object
myResult = jpylyzer.checkOneFile(myFile)

# Return image height value
imageHeight = myResult.findtext('./properties/jp2HeaderBox/imageHeaderBox/height')
print(imageHeight)
```

Here, *myResult* is an *Element* object that can either be used directly, 
or converted to XML using the *ElementTree* module[^3]. The structure of the
element object follows the XML output that described in [Chapter 5](#output-format).

For validation a raw JPEG 2000 codestreams, call the *checkOneFile* function with the additional
*validationFormat* argument, and set it to `j2c`:

```python
# Define Codestream
myFile = "/home/johan/jpylyzer-test-files/rubbish.j2c"

# Analyse with jpylyzer, result to Element object
myResult = jpylyzer.checkOneFile(myFile, 'j2c')
```

<!-- End of text to be copied to usage.md of jpylyzer website -->

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
