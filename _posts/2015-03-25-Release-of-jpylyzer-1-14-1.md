---
layout: post
title: Release of jpylyzer 1.14.1 
---
{% include JB/setup %}

Following a year of limited development activity, we proudly present *jpylyzer* 1.14.1. Here's an overview of the most noticeable changes in this version.

### Improved XML output

*Jpylyzer*'s output now  contains a namespace declaration as well as a reference to an XSD schema. The [schema can be found here](http://jpylyzer.openpreservation.org/jpylyzer-v-1-0.xsd). Hopefully these improvements will make post-processing *jpylyzer*'s output easier. Note that the schema has had limited testing so far, and it's not inconceivable that it may need further tweaking. If you get unexpected results (e.g. output files that are not valid against the schema) please let us know, preferably using the [issue tracker](https://github.com/openpreserve/jpylyzer/issues).

### Recursive scanning of directory trees

The new `--recurse` option allows you to recursively scan a directory tree. Read [this warning](http://jpylyzer.openpreservation.org//userManual.html#warning) before using this feature; for operational production settings it's probably safer not to use it yet. Thanks go out to Adam Retter, Jaishree Davey and Laura Damian of The National Archives (UK) who submitted this feature.

### User Manual changes

The User Manual is now accessible in two ways:

1. [online on the main website](http://jpylyzer.openpreservation.org/userManual.html);

2. as a [downloadable self-contained HTML file](http://jpylyzer.openpreservation.org/jpylyzerUserManual.html). This file is completely self-contained (all style sheets, images, etc. are embedded in one single file), which makes it suitable for offline viewing. This replaces the former PDF version, which is now discontinued. (With the source of the User Manual now being in MarkDown, generating PDF derivatives of acceptable quality turned out to be too much hassle.) Both versions are generated from the MarkDown source with this little [script](https://github.com/openpreserve/jpylyzer/blob/master/doc/mdToDeliveryFormats.sh).

### CLI argument parser fix

The helper message in the latest versions of *jpylyzer* was somewhat confusing because the argument parser library was called in an unusual way. This has also been fixed (*jpylyzer*'s behavior is unaffected by this).

### Vagrant virtual machine definitions and build scripts

The [Vagrant](https://github.com/openpreserve/jpylyzer/tree/master/vagrant) directory of the source repo allows you to automatically set up virtual machines for building 64 and 32 bit Debian packages using [*Vagrant*](http://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/).

### Miscellaneous fixes

Apart from the above changes, this release includes various minor tweaks, clean-ups and fixes; most of these are unnoticeable to the user.

### Final remarks

It's always possible that changes cause things to go wrong unintentionally; if this happens please get in touch, if possible using the [issue tracker](https://github.com/openpreserve/jpylyzer/issues). Meanwhile, happy jpylyzing!


