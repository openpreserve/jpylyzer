---
layout: page
title: Using jpylyzer
---
{% include JB/setup %}

<!-- Start of text to be copied from jpylyzer README.md -->

## Using jpylyzer from the command line

Calling *jpylyzer* in a command window without any arguments results in the following helper message:

```
usage: jpylyzer [-h] [--format FMT] [--mix {1,2}] [--nopretty]
            [--nullxml] [--recurse] [--packetmarkers] [--verbose]
            [--version] jp2In [jp2In ...]
```

### Positional arguments

|Argument|Description|
|:--|:--|
|`jp2In`|input image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux|

### Optional arguments

|Argument|Description|
|:--|:--|
|`[-h, --help]`|show help message and exit|
|`[--format FMT]`|validation format; allowed values are `jp2` (used by default) and `j2c` (which activates raw codestream validation)|
|`[--mix {1,2}]`|report additional output in NISO MIX format (version 1.0 or 2.0)|
|`[--nopretty]`|suppress pretty-printing of XML output|
|`[--nullxml]`|extract null-terminated XML content from XML and UUID boxes(doesn't affect validation)|
|`[--recurse, -r]`|when analysing a directory, recurse into subdirectories|
|`[--packetmarkers]`|Report packet-level codestream markers (plm, ppm, plt, ppt)|
|`[--verbose]`|report test results in verbose format|
|`[-v, --version]`|show program's version number and exit|

## Output

Output is directed to the standard output device (*stdout*).

## Examples

Validate JP2 image:

```
jpylyzer rubbish.jp2 > rubbish-jp2.xml`
```

Validate JPEG 2000 Part 1 codestream:

```
jpylyzer --format j2c rubbish.j2c > rubbish-j2c.xml`
```

Validate JPH (High Throughput) image:

```
jpylyzer --format jph rubbish.jph > rubbish-jph.xml`
```

Validate JPEG 2000 Part 15 (High Throughput) codestream:

```
jpylyzer --format jhc rubbish.jhc > rubbish-jhc.xml`
```

In the above examples, output is redirected to the output files &#8216;rubbish-???.xml&#8217;. By default *jpylyzer*&#8217;s XML is pretty-printed, so you should be able to view the file using your favourite text editor. Alternatively use a dedicated XML editor, or open the file in your web browser.

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

7. *warnings*: reported warnings

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
#! /usr/bin/env python3

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
or converted to XML using the *ElementTree* module[^3].

For validation a raw JPEG 2000 codestreams, call the *checkOneFile* function with the additional
*validationFormat* argument, and set it to `j2c`:

```python
# Define Codestream
myFile = "/home/johan/jpylyzer-test-files/rubbish.j2c"

# Analyse with jpylyzer, result to Element object
myResult = jpylyzer.checkOneFile(myFile, 'j2c')
```

<!-- End of text to be copied from jpylyzer README.md -->

## User Manual

For more detailed information on the use of *jpylyzer*, there&#8217;s an exhaustive [User Manual]({{ BASE_PATH }}/doc/latest/userManual.html). It provides an in-depth coverage of the following topics:

* the installation process;
* usage of *jpylyzer* as a command-line tool, or as an importable *Python* module;
* an overview of the box structure of a *JP2* file;
* *jpylyzer*&#8217;s output format;
* a description of *every* test that *jpylyzer* performs for validation;
* a description of *every* reported property.
