---
layout: post
title: Release of jpylyzer 1.18.0
---
{% include JB/setup %}

*Jpylyzer* 1.18.0 is out now. This is mainly a maintenance release without any new functionality. The main changes are:

* It is now possible to install *jpylyzer* using the [*pip*](https://en.wikipedia.org/wiki/Pip_(package_manager)) package manager. This makes installing *jpylyzer* on any platform as simple as typing:

        pip install jpylyzer

    More details can be found in the [User Manual]({{ BASE_PATH }}/userManual.html). Note that all previous installation methods (Debian packages, stand-alone Windows binaries) are still supported, and will remain so.

* The build process for building the Windows binaries has been simplified; Windows binaries can now be built under Linux using [Wine](https://www.winehq.org/) with no need for a dedicated Windows machine.

* A bug that would cause *jpylyzer* to report an internal error for images with an Intellectual Property Box is now fixed.

* Improved behaviour for codestream comments with binary content (patch by Adam Fritzler).

In addition to this the source repo was cleaned up in places. Some outdated build scripts were removed or brought up to date, and some outdated documentation was updated as well. The code now conforms to [PEP 8](https://www.python.org/dev/peps/pep-0008/) again. Also included is a patch by Stefan Weil which fixes a number of *pylint* warnings.
