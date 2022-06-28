---
layout: post
title: Jpylyzer 2.1.0 release
---
{% include JB/setup %}

We just released a first release candidate of *Jpylyzer* 2.1. This release only introduces some relatively minor changes, compared against the earlier 2.0 release.

## Reporting of packet-level codestream markers

Tim Lander of Hexagon Geospatial [submitted a contribution](https://github.com/openpreserve/jpylyzer/pull/170) that adds reporting of properties from the PLM and PLT marker segments (packet-length markers segments at the main header and tile-part level, respectively). Shortly afterwards, Aaron Boxer posted a [feature request for abbreviated output](https://github.com/openpreserve/jpylyzer/issues/185) on these very same PLT markers, as the PLT output would become excessive for large satellite images (which apparently always contain PLT markers, and lots of them!). 

To reconcile these (at first sight conflicting) needs, I added the new `--packetmarkers` command-line switch. This affects the following marker segments:

- Packet length, main header (PLM) marker segment
- Packet length, tile-part header (PLT) marker segment
- Packed packet headers, main header (PPM) marker segment
- Packed packet headers, tile-part header (PPT) marker segment

 By default, Jpylyzer 2.1 won't report detailed output on any of these packet-level codestream markers, but instead only report their number of occurrences. At the main header level these occurrences are reported using the new *plmCount* and *ppmCount* elements , and at the tile-part level using the *pltCount* and *pptCount* elements. Full output on individual packet-level markers is only reported if the user provides the `--packetmarkers` switch.

The newly updated [jpylyzer 2.1 XSD schema]({{ BASE_PATH }}/jpylyzer-v-2-1.xsd) reflects these changes.

## Automated unit tests using jpylyzer test corpus

We also made the release process more efficient by implementing unit tests based on the [jplyzer-test-files](https://github.com/openpreserve/jpylyzer-test-files) corpus.

## End of Python 2.7 support

Jpylyzer has always been compatible with both Python 3 and Python 2.7, but maintenance of Python 2.7 [stopped in 2020](https://pythonclock.org/). Because of this, Python 2.7 support will most likely be removed in Jpylyzer 2.2. This 2.1 release still works with Python 2.7 (you will see a deprecation warning), but we strongly urge you to upgrade to Python 3 if you haven't done so already.

## Miscellaneous changes

Finally, this release includes several small bug fixes, and some improvements to the documentation.

## Feedback

Any feedback on this *jpylyzer* release candidate is greatly appreciated. Also, don't hesitate to contact us if anything doesn't behave as expected (preferrably using the [issue tracker](https://github.com/openpreserve/jpylyzer/issues)).

Happy jpylyzing!
