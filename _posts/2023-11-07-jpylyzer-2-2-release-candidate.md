---
layout: post
title: Jpylyzer 2.2 release candidate
---
{% include JB/setup %}

We just released a first release candidate of Jpylyzer 2.2. This is quite an action-packed release, which even includes the addition of two new supported file formats! Below is an overview of the main changes.

## High Throughput JPEG 2000

Jpylyzer now supports [High Throughput JPEG 2000](https://jpeg.org/jpeg2000/htj2k.html) (HTJ2K) and its associated JPH file format. Both are defined in [Part 15 of the standard](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-T.814-201906-I!!PDF-E&type=items), which was first published in 2019. To validate a JPH file, use:

```
jpylyzer --format jph oj-ht-byte.jph > out-jph.xml
```

For a raw HTJ2K codestream, use this:

```
jpylyzer --format jhc oj-ht-byte_causal.jhc > out-jhc.xml
```

Note that not many encoders support HTJ2K at this stage, and the code has only been tested on a limited number of sample files. These files do not encompass all of HTJ2K's features. We encourage HTJ2K users to contribute additional files to the [Jpylyzer test files repository](https://github.com/openpreserve/jpylyzer-test-files), and [report](https://github.com/openpreserve/jpylyzer/issues) any unexpected behaviour.

## Additional codestream markers

This release also adds support for the Extended Capabilities (CAP) and Profile Marker (PRF) marker segments, which were introduced in the 2019 revision of JPEG 2000 Part 1, and the Corresponding Profile (CPF) marker segment, which is specific to JPEG 2000 Part 15 (High Throughput JPEG 2000).

## Reporting and validation of *rsiz* property

Previous versions of Jpylyzer reported the *rsiz* property as either a numerical value, or as a text string associated with that value. Changes to the use of the *rsiz* field since the first editions of the standard made this approach increasingly impractical. So, from version 2.2 onward, Jpylyzer always reports *rsiz* as a numerical value. In addition, it adds the new *capability* property, which contains the associated text string (which in most cases describes a defined profile). The coverage of these text strings / profiles is now also up to date with the 2019 version of the JPEG 2000 Part 1 standard, which means that many more profiles are reported. Finally, the validation of *rsiz* itself has been improved as well, as earlier Jpylyzer versions were overly restrictive on the allowed values.

## Reporting of warnings to output file

File-level warnings (e.g. in case of unknown boxes) are now included in a new "warnings" element in Jpylyzer's output. Previously, these were only written to the terminal's *stderr*.

## API improvements

All output and extraction options can now be set directly as Python API parameters, which will be helpful for those who want to integrate Jpylyzer in their own Python projects.

## Compression ratio reporting for codestreams

Previously Jpylyzer only reported the image compression ratio for JP2 files, and not for raw codestreams. This has changed, and the compression ratio is now reported for all supported formats (including codestreams).

## No Python 2.7 support

From this release onward, Jpylyzer now *only* works with Python 3. Python 2.7 is no longer supported, as we already [announced in 2019]({{ BASE_PATH }}/2019/11/20/Release-of-jpylyzer-2-0-0
) at the launch of Jpylyzer 2.0.

## Removed legacy options 

The deprecated `--wrapper` and `--legacyout` options have been removed in this release.

## Other changes

In addition to the above changes, this release also includes several bugfixes. There's also [a new XSD schema]({{ BASE_PATH }}/jpylyzer-v-2-2.xsd), and the documentation has been made up to date.

## Installation with pip

As the current release candidate is a pre-release, make sure to include the `--pre` option if you install it with pip. For example, for a fresh install use: 

```bash
pip install jpylyzer --pre
```

To upgrade an existing version of Jpylyzer, use:

```bash
pip install jpylyzer --upgrade --pre
```

## Installation from binaries

Alternatively, you can use the binaries that are available here: 

<https://github.com/openpreserve/jpylyzer/releases/tag/2.2.0rc1>

As always, the Windows binaries are completely stand-alone, and don’t require Python on your machine. Linux users can use the Debian package (which does require Python).

## User Manual

An updated User Manual for Jpylyzer 2.2 is [available here]({{ BASE_PATH }}/doc/2-2/userManual.html).

## Feedback

Any feedback on this Jpylyzer release candidate is greatly appreciated. Also, don't hesitate to contact us if anything doesn't behave as expected (preferrably using the [issue tracker](https://github.com/openpreserve/jpylyzer/issues)).

## Acknowledgments

Thanks are due to Aous Naman (University of New South Wales) and Osamu Watanabe (Takushoku University) for their help and suggestions on High Throughput JPEG 2000, and Michael D. Smith (Wavelet Consulting LLC) for providing one of the HTJ2K test images.

Happy jpylyzing!
