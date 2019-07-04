---
layout: page
title: Using jpylyzer
---
{% include JB/setup %}

## Using jpylyzer from the command line

Calling *jpylyzer* in a command window without any arguments results in the following helper message:

{% highlight console %}
usage: jpylyzer [-h] [--format FMT] [--legacyout] [--nopretty] [--nullxml]
                [--recurse] [--verbose] [--version] [--wrapper]
                jp2In [jp2In ...]
{% endhighlight %}

### Positional arguments

|:--|:--|
|`jp2In`|input JP2 image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux|


### Optional arguments

|:--|:--|
|`[-h, --help]`|show help message and exit|
|`[--format FMT]`|validation format; allowed values are `jp2` (used by default) and `j2c` (which activates raw codestream validation)|
|`[--legacyout]`|report output in jpylyzer 1.x format (provided for backward compatibility only)|
|`[--nopretty]`|suppress pretty-printing of XML output|
|`[--nullxml]`|extract null-terminated XML content from XML and UUID boxes(doesn't affect validation)|
|`[--recurse, -r]`|when analysing a directory, recurse into subdirectories (implies `--wrapper` if `--legacyout` is used)|
|`[--verbose]`|report test results in verbose format|
|`[-v, --version]`|show program's version number and exit|
|`[--wrapper, -w]`|wrap output for individual image(s) in 'results' XML element (deprecated from jpylyzer 2.x onward, only takes effect if `--legacyout` is used)|

## Output

Output is directed to the standard output device (*stdout*).

## Example

{% highlight console %}
jpylyzer rubbish.jp2 > rubbish.xml
{% endhighlight %}

In the above example, output is redirected to the file &#8216;rubbish.xml&#8217;. By default *jpylyzer*&#8217;s XML is pretty-printed, so you should be able to view the file using your favourite text editor. Alternatively use a dedicated XML editor, or open the file in your web browser.

## Overview of output elements

A *jpylyzer* output file contains the following top-level output elements:

1. *toolInfo* element: tool name (jpylyzer) + version.
2. one or more *file* elements: holds all information about the analysed file(s)

in turn, each *file* element holds the following child elements:

1. *fileInfo*: name, path, size and last modified time/date of input file.
2. *isValid*: *True* / *False* flag indicating whether file is valid.
4. *tests*: tree of test outcomes, expressed as *True* / *False* flags.
   A file is considered valid only if all tests return *True*. Tree follows JP2 box structure. By default only tests that returned *False* are reported, which results in an empty *tests*  element for files that are valid JP2. Use the  `--verbose` flag to get *all* test results.
5. *properties*: tree of image properties. Follows JP2 box structure. Naming of properties follows [ISO/IEC 15444-1 Annex I](https://web.archive.org/web/20100926184120/http://www.jpeg.org/public/15444-1annexi.pdf) (JP2 file format syntax) and [Annex A](http://www.itu.int/rec/T-REC-T.800/en) (Codestream syntax).

## Using jpylyzer as a Python module

In order to use *jpylyzer* in your own Python programs, first install it
with *pip*. Then import *jpylyzer* into your code by adding:

    from jpylyzer import jpylyzer

Subsequently you can call any function that is defined in *jpylyzer.py*.
In practice you will most likely only need the *checkOneFile* function. 
The following minimal script shows how this works:

    from jpylyzer import jpylyzer

    # Define JP2
    myFile = "/home/johan/jpylyzer-test-files/aware.jp2"

    # Analyse with jpylyzer, result to Element object
    myResult = jpylyzer.checkOneFile(myFile)

    # Return image height value
    imageHeight = myResult.findtext('./properties/jp2HeaderBox/imageHeaderBox/height')
    print(imageHeight)

Here, *myResult* is an *Element* object that can either be used directly, 
or converted to XML using the *ElementTree* module[^3]. The structure of the
element object follows the XML output that described in [Chapter 5](#output-format).

For validation a raw JPEG 2000 codestreams, call the *checkOneFile* function with the additional
*validationFormat* argument, and set it to `j2c`:

    # Define Codestream
    myFile = "/home/johan/jpylyzer-test-files/rubbish.j2c"

    # Analyse with jpylyzer, result to Element object
    myResult = jpylyzer.checkOneFile(myFile, 'j2c')

## Demonstration video

The following video gives an overview of what *jpylyzer* does, and how to use it:

<iframe src="{{ site.jpylyzerVideo }}" width="500" height="281" allowfullscreen></iframe>

Note that this video was based on an older *jpylyzer* version that didn&#8217;t support pretty-printed output. (From version 1.13.0 onward *jpylyzer* uses pretty-printing for its XML output.)

## User Manual

For more detailed information on the use of *jpylyzer*, there&#8217;s an exhaustive [User Manual]({{ BASE_PATH }}/userManual.html). It provides an in-depth coverage of the following topics:

* the installation process;
* usage of *jpylyzer* as a command-line tool, or as an importable *Python* module;
* an overview of the box structure of a *JP2* file;
* *jpylyzer*&#8217;s output format;
* a description of *every* test that *jpylyzer* performs for validation;
* a description of *every* reported property.
