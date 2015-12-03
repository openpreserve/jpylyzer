---
layout: post
title: Release of jpylyzer 1.15.1 
---
{% include JB/setup %}

Version 1.15.1 of *jpylyzer* is now available. The most notable improvement in this release is the use of [memory mapping](https://en.wikipedia.org/wiki/Memory-mapped_file) for reading input images. This results in better performance when processing (very) large files. This improvement was suggested by Stefan Weil of Mannheim University Library, and the changes are based on a patch he submitted.

Two examples illustrate the benefits of this change:

* [This 2 GB image](http://hirise-pds.lpl.arizona.edu/download/PDS/RDR/ESP/ORB_011200_011299/ESP_011265_1560/ESP_011265_1560_RED.JP2)
 resulted in a memory error with *jpylyzer* 1.14.2 on a Windows machine with 4 GB RAM. The new version processes the file without problems.

* On a Linux Mint machine with 8 GB RAM, [this 6.7 GB image](http://apollo.sese.asu.edu/data/pancam/AS16/jp2/AS16-P-4102.jp2)
 also resulted in a memory error. Again, the new version handles the file without any problem. 

Please bear in mind that memory errors may still occur under some circumstances. For instance, a test with the 6.7 GB image failed on a Linux Mint machine with 4 GB RAM. So it seems prudent to make sure that the amount of available RAM always exceeds the maximum image size by a fairly wide safety margin. Also, chip architecture and operating system may put further constraints on the amount of memory than can be mapped at a time. 
 
Memory errors aside, the processing of large files like the above is also quite a bit faster than in earlier releases, and it is less prone to freezing other processes that are running on your machine.

This release also fixes a number of minor bugs, most notably:

* A [Python runtime error](https://github.com/openpreserve/jpylyzer/pull/72) that would occur for some corrupted JP2s (patch again by Stefan Weil).

* Under Python 3, the validation test *locHasNullTerminator* [would erroneously fail](https://github.com/openpreserve/jpylyzer/issues/76) for JP2s with an URL  Box. 

