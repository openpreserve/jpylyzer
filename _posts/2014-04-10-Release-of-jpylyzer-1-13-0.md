---
layout: post
title: Release of jpylyzer 1.13.0 
---
{% include JB/setup %}

Since it&#8217;s been quite a while since the previous binary release (which was version 1.10.1), here&#8217;s a brief overview of the main changes since that version:

###Pretty-printed output
The most visible change is that *jpylyzer* now produces output as pretty-printed XML. If you&#8217;re using *jpylyzer* interactively, you can now inspect its output without the need to use a dedicated XML editor or viewer; just use any text editor you like. You can suppress pretty printing with the *--nopretty* option.

###Improved stability in case of malformed images
Andy Jackson of the British Library reported some [odd behaviour](https://github.com/openplanets/jpylyzer/issues/31) with images that were (deliberately) malformed by flipping specific bit values. An analysis revealed a number of edge cases that would drive *jpylyzer* into an (almost) infinite loop. Although  you&#8217;re unlikely to run into such malformations with actual images that exist &#8216;in the wild&#8217;, *jpylyzer* now handles these cases gracefully.

###Extraction of null-terminated XML content
Old versions of certain *JPEG 2000* encoders would erroneously terminate embedded XML with a null byte. As this results in an XML (or UUID) box whose contents are not well-formed XML, *jpylyzer* doesn&#8217;t include the XML in its output if this happens. The new *--nullxml* option forces *jpylyzer* to extract the XML (minus the trailing null byte) in that case. The use of this option does *not* affect the validation outcome in any way.

###Validation of codestream comments
*Jpylyzer* now includes a check on the presence of control characters in codestream comments.

###Validation of URL box
URLs in the URL box must be terminated with a null-byte; *jpylyzer* now performs a check for this.  
 
###Improved handling of control characters and UTF-8
This release also fixes a number of minor bugs that are related to the handling of control characters in extracted content, and the subsequent encoding of extracted features as UTF-8 encoded text.

###Miscellaneous bugfixes and improvements
In addition to the above changes, this release contains a number of small fixes, improvements and optimisations, most of which are invisible to the user. Also, the source code now (mostly) respects the conventions of the [PEP 8](http://legacy.python.org/dev/peps/pep-0008/) style guide, which should make it easier to read.

##Improved build process, more regular releases
For some time the release schedule of binary packages for *jpylyzer* has been lagging behind the development version for quite a bit. The main reason for this was the somewhat awkward process for making the Debian packages: each release includes both 64 and 32 bit packages, each of which needs to be built on a different architecture.

A recent [SCAPE training event](http://wiki.opf-labs.org/display/SP/SCAPE+Training+Event+-+Preserving+Your+Preservation+Tools) gave me the idea of creating each build using a dedicated virtual machine, which is pretty easy with [*VirtualBox*](https://www.virtualbox.org/) and [*Vagrant*](http://www.vagrantup.com/). That didn&#8217;t *quite* work, as *VirtualBox* turned out to be unable to cope with any 64-bit virtual machines (which is probably a quirk of the host machine I&#8217;m using for the builds, which is quite old). In the end I decided on doing a clean install of [*Linux Mint* 13](http://www.linuxmint.com/release.php?id=18) on the host machine (based on [*Ubuntu* 12.04 *Precise*](http://releases.ubuntu.com/12.04/)), and this machine is used directly for creating the 64 bit packages. The 32 bit packages are made on a virtual machine running the 32 bit version of *Ubuntu Precise*.

Finally the *Windows* executables are made on a separate machine, as always. Overall this results in a workflow that is reasonably straightforward. This should result in more regular binary releases from now on.

