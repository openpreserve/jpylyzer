---
layout: post
title: Jpylyzer 2.3 release candidate
---
{% include JB/setup %}

We just released the first release candidate of Jpylyzer 2.3. Although this release does introduce some new features, most of the changes are aimed at
improving the maintainability of the code base, and streamlining the release process. Below is an overview of the main changes.

## Tile-part lengths marker segment

This release adds support for parsing and validating the tile-part lengths marker (TLM) segment, through a contribution by Jérémy Boisseau (Deluxe).

## ICC profile improvements

Previously, Jpylyzer was unable to parse the "profileDescriptionTag" of v.4 ICC profiles, which resulted in an empty "description" element. This has been fixed
in this release. In addition, Jpylyzer now also reports the information from the "copyrightTag", "mediaWhitePointTag" and "chromaticAdaptationTag". This means
that all tags that are mandatory for all profiles are now covered..

## Code organisation

Previously, all code for parsing and validating JP2/JPH/JP2C/JHC files was stored in one massive 3700-line "BoxValidator" class. This was getting increasingly
impractical, and it made maintaining the code unnecessarily hard. Starting with this release, the validator functions are spread across six smaller modules, each of which contains a validator class:

- *jp2.py* - Top-level JP2 / JPH validation (class *JP2Validator*)
- *boxes.py* - Validation of all defined boxes for JP2 and JPH (class *BoxValidator*)
- *codestream.py* - JPEG 2000 codestream validation (class *CSValidator*)
- *tilepart.py* - Validation of one tile part of a JPEG 2000 codestream (class *TilePartValidator*)
- *csmarkers.py* - Validation of JPEG 2000 codestream marker segments (class *CSMarkerValidator*)
- *icc.py* - Feature extraction from an ICC profile (class *IccValidator*)

These validator classes are all child classes of a generic *Validator* parent class (which is defined in the new *validator.py* module).

## Packaging improvements

This release also introduces some changes to the packaging processes: 

- Previously the Windows executables were built in a Dockerized Linux container, which used [Wine](https://www.winehq.org/) to run a Windows version of Python. This build process used an ancient (3.7) Python version. Since more recent Python versions don't work well with Wine, the build process has been replaced by one that runs on an actual Windows 11 (virtual) machine, using a modern (3.14) version of Python instead.
- The Docker-based build process for Debian packages has been adapted to address some compatibility issues with current Docker versions.
- The Docker-based script for creating and uploading packages to the Python Package Index has been replaced by a simpler one that does not use Docker at all.

## Other changes

In addition to the above changes, this release includes several bugfixes. There's also [a new XSD schema]({{ BASE_PATH }}/jpylyzer-v-2-3.xsd), and the documentation has been made up to date.

## Installation from Python package index

As of 2026, [uv](https://docs.astral.sh/uv/) appears to be the most straightforward tool for installing Python applications from the Python Package Index. Instructions on how to install uv are available [here](https://docs.astral.sh/uv/getting-started/installation/).

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
