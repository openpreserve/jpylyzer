---
layout: page
title: Using jpylyzer
---
{% include JB/setup %}

## Using jpylyzer
Calling *jpylyzer* in a command window without any arguments results in the following helper message:

{% highlight console %}
jpylyzer [-h] [--verbose] [--wrapper] [--version] ...
{% endhighlight %}

### Positional arguments
`...` : input JP2 image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux..

### Optional arguments

`-h, --help` : show this help message and exit;

`-v, --version` : show program's version number and exit;

`--verbose` : report test results in verbose format;

`--wrapper, -w` : wrap the output for individual image(s) in 'results' XML element.

## Output 
Output is directed to the standard output device (*stdout*).

## Example

{% highlight console %}
jpylyzer rubbish.jp2 > rubbish.xml
{% endhighlight %}

In the above example, output is redirected to the file &#8216;rubbish.xml&#8217;. Note that currently *jpylyzer*&#8217;s XML is not pretty-printed, so you may want to use an XML editor to view the output (or open the XML in your web browser).

## Overview of output elements
A *jpylyzer* output file contains the following top-level output elements:

1. *toolInfo*: tool name (jpylyzer) + version.
2. *fileInfo*: name, path, size and last modified time/date of input file.
3. *isValidJP2*: *True* / *False* flag indicating whether file is valid JP2.
4. *tests*: tree of test outcomes, expressed as *True* / *False* flags.
   A file is considered valid JP2 only if all tests return *True*. Tree follows JP2 box structure. By default only tests that returned *False* are reported, which results in an empty *tests*  element for files that are valid JP2. Use the  `--verbose` flag to get *all* test results.
5. *properties*: tree of image properties. Follows JP2 box structure. Naming of properties follows [ISO/IEC 15444-1 Annex I](http://www.jpeg.org/public/15444-1annexi.pdf) (JP2 file format syntax) and [Annex A](http://www.itu.int/rec/T-REC-T.800/en) (Codestream syntax).

## User Manual
For more information on the use of *jpylyzer*, have a look at the exhaustive [User Manual]({{ site.userManualURL }}). It provides an in-depth coverage of the following topics:

* the installation process;
* usage of *jpylyzer* as a command-line tool, or as an importable *Python* module;
* an overview of the box structure of a *JP2* file;
* *jpylyzer*&#8217;s output format;
* a description of *every* test that *jpylyzer* performs for validation;
* a description of *every* reported property.
