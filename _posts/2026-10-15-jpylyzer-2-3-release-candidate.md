---
layout: post
title: Jpylyzer 2.3 release candidate
---
{% include JB/setup %}

We just released the first release candidate of Jpylyzer 2.3. Below is an overview of the main changes.

## Tile-part lengths marker segment

This release adds support for parsing and validating the tile-part lengths marker (TLM) segment, through a contribution by Jérémy Boisseau (Deluxe).

## ICC profile improvements

Previously, Jpylyzer was unable to parse the "profileDescriptionTag" of v.4 ICC profiles, which resulted in an empty "description" element. This has been fixed
in this release. In addition, Jpylyzer now also reports the information from the "copyrightTag", "mediaWhitePointTag" and "chromaticAdaptationTag". This means
that all tags that are mandatory for all profiles are now covered..

## Other changes

In addition to the above changes, this release also includes several bugfixes. There's also [a new XSD schema]({{ BASE_PATH }}/jpylyzer-v-2-3.xsd), and the documentation has been made up to date.

## Installation from Python package index

As of 2026, [uv](https://docs.astral.sh/uv/) appears to be the most straightforward tool
for installing Python applications from the Python Package Index. Instructions on how to install uv are available [here](https://docs.astral.sh/uv/getting-started/installation/).

Use the following command to install the pre-release:

```
uv tool install --prerelease allow jpylyzer
```

## Installation from binaries

Alternatively, you can use the binaries that are available here: 

<https://github.com/openpreserve/jpylyzer/releases/tag/2.3.0rc1>

As always, the Windows binaries are completely stand-alone, and don’t require Python on your machine. Linux users can use the Debian package (which does require Python).

## User Manual

An updated User Manual for Jpylyzer 2.3 is [available here]({{ BASE_PATH }}/doc/2-3/userManual.html).

## Feedback

Any feedback on this Jpylyzer release candidate is greatly appreciated. Also, don't hesitate to contact us if anything doesn't behave as expected (preferrably using the [issue tracker](https://github.com/openpreserve/jpylyzer/issues)).

Happy jpylyzing!
