---
layout: post
title: Jpylyzer 2.0.0 release
---
{% include JB/setup %}

We just released *Jpylyzer* 2.0.0. Unlike previous releases, this is a major release that introduces some breaking changes with respect to previous versions. Below is a short overview of the main changes.

## Validation of raw codestreams

*Jpylyzer* is now capable of validating 'raw' [JPEG 2000 codestreams](http://fileformats.archiveteam.org/wiki/JPEG_2000_codestream). Codestream validation can be activated by setting the new `--format` switch to value `j2c`. When *jpylyzer* is used as a Python module, use the *checkOneFile* function's new *validationFormat* argument and set it to `j2c` (e.g. `myResult = jpylyzer.checkOneFile(myFile, 'j2c')`). Although raw codestreams are pretty rare in the wild, having the ability to validate codestreams can be useful for validating individual JPEG 2000 encoded frames that are wrapped inside video containers. Note that the parsing of any video container formats is the responsibility of the user, as this is not supported by *jpylyzer*.

## MIX output

It is now possible to report additional output in [*NISO MIX*](http://www.loc.gov/standards/mix/) format using the new  `--mix` option. The MIX functionality was developed by Thomas Ledoux of Bibliothèque nationale de France.

## Support for additional codestream marker segments

This release adds support for the following (optional) codestream marker segments:

- COC (Code style component)

- QCC (Quantization component)

- POC (Progression order change)

- RGN (Region of interest)

- CRG (Component registration)

These marker segments are now fully parsed and validated, and their associated properties are included in the output (previous versions would simply report the presence of these markers as empty elements). 


## Changes to the output format

The addition of the codestream validation option made it necessary to make some changes to *jpylyzer*'s output format that break compatibility with previous versions. Since there was no way to avoid some breaking changes anyway, we decided to take this as an opportunity to address some further inconsistencies in *jpylyzer*'s output format. The changes are:

1. The *isValidJP2* element is superseded by the new *isValid* element. This element has a *format* attribute which defines the validation format, which is either `jp2` or `j2c` (in the case of a codestream).

2. The top-level output element is now *always* `<jpylyzer>` (confusingly, previous versions would add a `<results>` element if either the `--wrapper` or `--recurse` options were activated). This top-level element contains one `<toolInfo>` element, and one or more `<file>` elements. Each `<file>` element then contains the usual `<fileInfo>`, `<statusInfo>`, `<isValid>`, `<tests>` and `<properties>` elements. The `--wrapper` option has been deprecated (since the output of each analysed file is now wrapped by default).

3. The reported values of the *precincts* property have been changed to “default” (previously: “no”) and “user defined” (previously: “yes”). The old values falsely suggested that precincts were altogether absent in “default” case. 

4. Precinct size (*precinctSizeX*, *precinctSizeX*) values are now also reported for the “default” case (see above). 

5. If the `--mix` option is used, *MIX* output is written to a new *propertiesExtension* element inside the *properties* element.

For more details, have a look at the [jpylyzer 2.0 XSD schema]({{ BASE_PATH }}/jpylyzer-v-2-0.xsd).

## Backward compatibility

Since the new output format will break existing workflows that expect *jpylyzer* 1.x output, we added a `--legacyout` option that results in output that follows the old 1.x format. Note that codestream validation and the reporting of MIX output are disabled if this option is used!

## Archive of old User Manuals

We have also added a [*User Manual Archive*]({{ BASE_PATH }}/doc/) to this website, which contains the User Manuals of all previous *jpylyzer* releases up to version 1.14 (this was the first release with the current HTML-formatted documentation).

## Packaging

The packaging workflows for both the Windows binaries and the Debian packages have been given an overhaul. One of the implications of these changes is that there is no longer any need for separate 32- and 64-bit Debian packages. Instead, the new packages work with both architectures. However, unlike the 'old-style' packages, which were completely stand-alone, the new packages do require Python 3. As per the [Debian Python Policy](https://www.debian.org/doc/packaging-manuals/python-policy/ch-python3.html) we don't offer packages that use Python 2 (which [will not be maintained pas january 2020](https://pythonclock.org/)).

## Continuous integration improvements

In addition to the above changes, which are all directly visible to the user of the software, a lot of development effort has been dedicated to automating various components of the *jpylyzer* release process. This includes static code analysis and the addition of automated tests. In particular:

- In order to better assess the quality of pull requests, code is now automatically checked for compliance against [*PEP 8*](https://www.python.org/dev/peps/pep-0008/) and [*PEP 257*](https://www.python.org/dev/peps/pep-0257/). Code is also analysed with [*Pylint*](https://www.pylint.org/). In addition to this, the existing code base has been been cleaned up in places to improve the compliance to these standards.

- A basic framework was set up for running unit tests. This makes it possible to create automated tests using files from the [*jpylyzer-test-files*](https://github.com/openpreserve/jpylyzer-test-files) corpus (the addition of any actual tests will follow in the near future).

## Note on Python 2 support

From its inception, *jpylyzer* has been compatible with both Python 2 and Python 3. This is still the case with the current release, but as [maintenance of Python 2 will stop in january 2020](https://pythonclock.org/), we strongly recommend to run (and install) *jpylylyzer* under Python 3. In future versions of *jpylyzer* we will most likely remove support for Python 2 altogether.

## Feedback

Any feedback on this *jpylyzer* release candidate is greatly appreciated. Also, don't hesitate to contact us if any of the (new) packages for some reason do not behave as expected (preferrably using the [issue tracker](https://github.com/openpreserve/jpylyzer/issues)).

Happy jpylyzing!
