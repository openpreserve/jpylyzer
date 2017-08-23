---
layout: post
title: Release of jpylyzer 1.18.0
---
{% include JB/setup %}

*Jpylyzer* 1.18.0 (AKA the "delayed 2017 spring clean-up release") is out now. The most notable change is that it is now possible to install *jpylyzer* with the [*pip*](https://en.wikipedia.org/wiki/Pip_(package_manager)) package manager. This makes installing *jpylyzer* on any platform as simple as typing:

    pip install jpylyzer

More details can be found in the [User Manual]({{ BASE_PATH }}/userManual.html). Note that all previous installation methods (Debian packages, stand-alone Windows binaries) are still supported, and will remain so.

Most other changes in this release are 'under the hood' and therefore less notable to most users:

* The build process for building the Windows binaries has been simplified; Windows binaries are now built under Linux using [Wine](https://www.winehq.org/) with no need for a dedicated Windows machine.

* Some modifications were made to the file and directory structure of the source repo. This was done to avoid problems with relative imports for the different packaging methods. The repo now also adheres more closely to established Python practices.

* In addition to this, the source repo was cleaned up in places. Some outdated build scripts were removed or brought up to date, and outdated documentation was updated as well. The code now conforms to [PEP 8](https://www.python.org/dev/peps/pep-0008/) again. Also, several (mostly stylistic) improvements were made based on an automatic analysis of the code with [Pylint](https://www.pylint.org/). This was prompted by an initial patch by Stefan Weil.

* Thanks to a patch by Adam Fritzler the behaviour for codestream comments with binary content has been improved.

Finally this release fixes two bugs:

* A bug that would cause *jpylyzer* to report an internal error for images with an Intellectual Property Box is now fixed.

* Another bug that would cause a Unicode error in Python 3 for filenames with [surrogate pair characters](http://unicodebook.readthedocs.io/unicode_encodings.html#surrogates) is fixed as well.

As always, any feedback on this new *jpylyzer* is appreciated. 


