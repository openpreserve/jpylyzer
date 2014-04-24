![](jpylyzerUserManual_files/image001.jpg)

![](jpylyzerUserManual_files/image002.jpg)

 

 

 

 

  

jpylyzer: validator and properties extractor for JPEG 2000 Part 1 (JP2)

User Manual

 

jpylyzer version: 1.13

 

 

 

 

 

 

 

 

Johan van der Knijff

KB/ National Library of the Netherlands

Open Planets Foundation

 

 

 

 

 

 

 

![scapelogo-big\_png.jpg](jpylyzerUserManual_files/image003.gif)This
work was partially supported by the SCAPE Project. The SCAPE project is
co-funded by the European Union under FP7 ICT-2009.4.1 (Grant Agreement
number 270137).

*  
*

  

Disclaimer

Both the program code and this manual have been carefully inspected
before printing. However, no warranties, either expressed or implied,
are made concerning the accuracy, completeness, reliability, usability,
performance, or fitness for any particular purpose of the information
contained in this manual, to the software described in this manual, and
to other material supplied in connection therewith. The material is
provided "as is". The entire risk as to its quality and performance is
with the user.

  

  

 

**Table of Contents**

 

 

[1������ Introduction. 1](#_Toc381698578)

[1.1������� About jpylyzer. 1](#_Toc381698579)

[1.2������� Validation: scope and restrictions. 1](#_Toc381698580)

[�Valid� means �probably valid� 1](#_Toc381698581)

[No check on compressed bitstreams. 1](#_Toc381698582)

[Recommendations for use in quality assurance workflows.
2](#_Toc381698583)

[Note on ICC profile support 2](#_Toc381698584)

[1.3������� Outline of this User Manual 2](#_Toc381698585)

[1.4������� Funding. 2](#_Toc381698586)

[1.5������� License. 2](#_Toc381698587)

[2������ Installation and set-up. 3](#_Toc381698588)

[2.1������� Obtaining the software. 3](#_Toc381698589)

[2.2������� Installation of Python script (Linux/Unix, Windows, Mac OS
X) 3](#_Toc381698590)

[Testing the installation. 3](#_Toc381698591)

[Troubleshooting. 4](#_Toc381698592)

[2.3������� Installation of Windows binaries (Windows only)
4](#_Toc381698593)

[Testing the installation. 4](#_Toc381698594)

[Running jpylyzer without typing the full path. 5](#_Toc381698595)

[2.4������� Installation of Debian packages (Ubuntu/Linux)
5](#_Toc381698596)

[3������ Using *jpylyzer*. 7](#_Toc381698597)

[3.1������� Overview.. 7](#_Toc381698598)

[3.2������� Command-line usage. 7](#_Toc381698599)

[Synopsis. 7](#_Toc381698600)

[Output redirection. 8](#_Toc381698601)

[Creating well-formed XML with multiple images. 8](#_Toc381698602)

[�nullxml� option. 8](#_Toc381698603)

[User warnings. 8](#_Toc381698604)

[3.3������� Using *jpylyzer* as a Python module. 9](#_Toc381698605)

[4������ Structure of a JP2 file. 11](#_Toc381698606)

[4.1������� Scope of this chapter. 11](#_Toc381698607)

[4.2������� General format structure. 11](#_Toc381698608)

[4.3������� General structure of a box. 12](#_Toc381698609)

[4.4������� Defined boxes in JP2. 12](#_Toc381698610)

[5������ Output format 15](#_Toc381698611)

[5.1������� Overview.. 15](#_Toc381698612)

[5.2������� toolInfo element 16](#_Toc381698613)

[5.3������� fileInfo element 16](#_Toc381698614)

[5.4������� isValidJP2 element 16](#_Toc381698615)

[5.5������� tests element 16](#_Toc381698616)

[Default and verbose reporting of test results. 17](#_Toc381698617)

[5.6������� properties element 17](#_Toc381698618)

[6������ JP2: box by box. 19](#_Toc381698619)

[6.1������� About the properties and tests trees. 19](#_Toc381698620)

[Naming of properties. 19](#_Toc381698621)

[6.2������� JPEG 2000 Signature box. 19](#_Toc381698622)

[Element name. 19](#_Toc381698623)

[Reported properties. 19](#_Toc381698624)

[Tests. 20](#_Toc381698625)

[6.3������� File Type box. 20](#_Toc381698626)

[Element name. 20](#_Toc381698627)

[Reported properties. 20](#_Toc381698628)

[Tests. 20](#_Toc381698629)

[6.4������� JP2 Header box (superbox) 20](#_Toc381698630)

[Element name. 20](#_Toc381698631)

[Reported properties. 20](#_Toc381698632)

[Tests. 21](#_Toc381698633)

[6.5������� Image Header box (child of JP2 Header box)
21](#_Toc381698634)

[Element name. 21](#_Toc381698635)

[Reported properties. 22](#_Toc381698636)

[Tests. 22](#_Toc381698637)

[6.6������� Bits Per Component box (child of JP2 Header box)
22](#_Toc381698638)

[Element name. 22](#_Toc381698639)

[Reported properties. 22](#_Toc381698640)

[Tests. 23](#_Toc381698641)

[6.7������� Colour Specification box (child of JP2 Header box)
23](#_Toc381698642)

[Element name. 23](#_Toc381698643)

[Reported properties. 23](#_Toc381698644)

[Reported properties of ICC profiles. 23](#_Toc381698645)

[Tests. 25](#_Toc381698646)

[6.8������� Palette box (child of JP2 Header box) 25](#_Toc381698647)

[Element name. 25](#_Toc381698648)

[Reported properties. 25](#_Toc381698649)

[Tests. 26](#_Toc381698650)

[6.9������� Component Mapping box (child of JP2 Header box)
26](#_Toc381698651)

[Element name. 26](#_Toc381698652)

[Reported properties. 26](#_Toc381698653)

[Tests. 26](#_Toc381698654)

[6.10����� Channel Definition box (child of JP2 Header box)
26](#_Toc381698655)

[Element name. 26](#_Toc381698656)

[Reported properties. 27](#_Toc381698657)

[Tests. 27](#_Toc381698658)

[6.11����� Resolution box (child of JP2 Header box, superbox)
27](#_Toc381698659)

[Element name. 27](#_Toc381698660)

[Reported properties. 27](#_Toc381698661)

[Tests. 27](#_Toc381698662)

[6.12����� Capture Resolution box (child of Resolution box)
28](#_Toc381698663)

[Element name. 28](#_Toc381698664)

[Reported properties. 28](#_Toc381698665)

[Tests. 28](#_Toc381698666)

[6.13����� Default Display Resolution box (child of Resolution box)
29](#_Toc381698667)

[Element name. 29](#_Toc381698668)

[Reported properties. 29](#_Toc381698669)

[Tests. 30](#_Toc381698670)

[6.14����� Contiguous Codestream box. 30](#_Toc381698671)

[6.15����� Intellectual Property box. 30](#_Toc381698672)

[6.16����� XML box. 30](#_Toc381698673)

[Element name. 30](#_Toc381698674)

[Reported properties. 30](#_Toc381698675)

[Tests. 30](#_Toc381698676)

[6.17����� UUID box. 31](#_Toc381698677)

[Element name. 31](#_Toc381698678)

[Reported properties. 31](#_Toc381698679)

[Tests. 31](#_Toc381698680)

[6.18����� UUID Info box (superbox) 32](#_Toc381698681)

[Element name. 32](#_Toc381698682)

[Reported properties. 32](#_Toc381698683)

[Tests. 32](#_Toc381698684)

[6.19����� UUID List box (child of UUID Info box) 32](#_Toc381698685)

[Element name. 32](#_Toc381698686)

[Reported properties. 32](#_Toc381698687)

[Tests. 32](#_Toc381698688)

[6.20����� Data Entry URL box (child of UUID Info box)
32](#_Toc381698689)

[Element name. 33](#_Toc381698690)

[Reported properties. 33](#_Toc381698691)

[Tests. 33](#_Toc381698692)

[6.21����� Unknown box. 33](#_Toc381698693)

[Element name. 33](#_Toc381698694)

[Reported properties. 33](#_Toc381698695)

[6.22����� Top-level tests and properties. 33](#_Toc381698696)

[Element name. 33](#_Toc381698697)

[Reported properties. 34](#_Toc381698698)

[Tests. 35](#_Toc381698699)

[7������ Contiguous Codestream box. 37](#_Toc381698700)

[7.1������� General codestream structure. 37](#_Toc381698701)

[Markers and marker segments. 37](#_Toc381698702)

[General structure of the codestream.. 37](#_Toc381698703)

[7.2������� Limitations of codestream validation. 38](#_Toc381698704)

[Main codestream header. 38](#_Toc381698705)

[Tile parts. 39](#_Toc381698706)

[Bit streams. 40](#_Toc381698707)

[Detection of incomplete or truncated codestreams. 40](#_Toc381698708)

[Current limitations of comment extraction. 40](#_Toc381698709)

[7.3������� Structure of reported output 40](#_Toc381698710)

[7.4������� Contiguous Codestream box. 41](#_Toc381698711)

[Element name. 41](#_Toc381698712)

[Reported properties. 41](#_Toc381698713)

[Tests. 42](#_Toc381698714)

[7.5������� Image and tile size (SIZ) marker segment (child of
Contiguous Codestream box) 43](#_Toc381698715)

[Element name. 43](#_Toc381698716)

[Reported properties. 43](#_Toc381698717)

[Tests. 44](#_Toc381698718)

[7.6������� Coding style default (COD) marker segment
45](#_Toc381698719)

[Element name. 45](#_Toc381698720)

[Reported properties. 45](#_Toc381698721)

[Tests. 46](#_Toc381698722)

[7.7������� Quantization default (QCD) marker segment
47](#_Toc381698723)

[Element name. 47](#_Toc381698724)

[Reported properties. 47](#_Toc381698725)

[Tests. 47](#_Toc381698726)

[7.8������� Comment (COM) marker segment 48](#_Toc381698727)

[Element name. 48](#_Toc381698728)

[Reported properties. 48](#_Toc381698729)

[Tests. 48](#_Toc381698730)

[7.9������� Tile part (child of Contiguous Codestream box)
49](#_Toc381698731)

[Element name. 49](#_Toc381698732)

[Reported properties. 49](#_Toc381698733)

[Tests. 49](#_Toc381698734)

[7.10����� Start of tile part (SOT) marker segment (child of tile part)
49](#_Toc381698735)

[Element name. 49](#_Toc381698736)

[Reported properties. 50](#_Toc381698737)

[Tests. 50](#_Toc381698738)

[7.11����� Coding style component (COC) marker segment
50](#_Toc381698739)

[Element name. 50](#_Toc381698740)

[Reported properties. 50](#_Toc381698741)

[Tests. 50](#_Toc381698742)

[7.12����� Region-of-interest (RGN) marker segment 51](#_Toc381698743)

[Element name. 51](#_Toc381698744)

[Reported properties. 51](#_Toc381698745)

[Tests. 51](#_Toc381698746)

[7.13����� Quantization component (QCC) marker segment
51](#_Toc381698747)

[Element name. 51](#_Toc381698748)

[Reported properties. 51](#_Toc381698749)

[Tests. 51](#_Toc381698750)

[7.14����� Progression order change (POC) marker segment
51](#_Toc381698751)

[Element name. 51](#_Toc381698752)

[Reported properties. 52](#_Toc381698753)

[Tests. 52](#_Toc381698754)

[7.15����� Packet length, main header (PLM) marker segment
52](#_Toc381698755)

[Element name. 52](#_Toc381698756)

[Reported properties. 52](#_Toc381698757)

[Tests. 52](#_Toc381698758)

[7.16����� Packed packet headers, main header (PPM) marker segment
52](#_Toc381698759)

[Element name. 52](#_Toc381698760)

[Reported properties. 52](#_Toc381698761)

[Tests. 53](#_Toc381698762)

[7.17����� Tile-part lengths (TLM) marker segment 53](#_Toc381698763)

[Element name. 53](#_Toc381698764)

[Reported properties. 53](#_Toc381698765)

[Tests. 53](#_Toc381698766)

[7.18����� Component registration (CRG) marker segment
53](#_Toc381698767)

[Element name. 53](#_Toc381698768)

[Reported properties. 53](#_Toc381698769)

[Tests. 53](#_Toc381698770)

[7.19����� Packet length, tile-part header (PLT) marker segment
54](#_Toc381698771)

[Element name. 54](#_Toc381698772)

[Reported properties. 54](#_Toc381698773)

[Tests. 54](#_Toc381698774)

[7.20����� Packed packet headers, tile-part header (PPT) marker segment
54](#_Toc381698775)

[Element name. 54](#_Toc381698776)

[Reported properties. 54](#_Toc381698777)

[Tests. 54](#_Toc381698778)

[8������ References. 55](#_Toc381698779)

 

  

  

1               Introduction
============================

 

1.1         About jpylyzer
--------------------------

This User Manual documents *jpylyzer*, a validator and feature extractor
for JP2 images.� JP2 is the still image format that is defined by JPEG
2000 Part 1 (ISO/IEC 15444-1).� *Jpylyzer* was specifically created to
answer the following questions that you might have about any JP2 file:

1.       Is this really a JP2 and does it really conform to the format's
specifications (validation)?

2.       What are the technical characteristics of this image (feature
extraction)?

1.2         Validation: scope and restrictions
----------------------------------------------

Since the word �validation� means different things to different people,
a few words about the overall scope of *jpylyzer*. First of all, it is
important to stress that *jpylyzer* is not a �one stop solution� that
will tell you that an image is 100% perfect. What *jpylyzer* does is
this: based on the JP2 format specification (ISO/IEC 15444-1), it parses
a file. It then subjects the file�s contents to a large number of tests,
each of which is based on the requirements and restrictions that are
defined by the standard. If a file fails one or more tests, this implies
that it does not conform to the standard, and is no valid JP2.
Importantly, this presumes that *jpylyzer*�s tests accurately reflect
the format specification, without producing false positives.

### �Valid� means �probably valid�

If a file passes all tests, this is an indication that it is *probably*
valid JP2. This (intentionally) implies a certain degree of remaining
uncertainty, which is related to the following.

First of all, *jpylyzer* (or any other format validator for that matter)
�validates� a file by trying to prove that it does *not* conform to the
standard. It cannot prove that that a file *does* conform to the
standard.

Related to this, even though *jpylyzer*�s validation process is very
comprehensive, it is not complete. For instance, the validation of JPEG
2000 codestreams at this moment is still somewhat limited. Section 7.2
discusses these limitations in detail. Some of these limitations (e.g.
optional codestream segment markers that are only minimally supported at
this stage) may be taken away in upcoming versions of the tool.

### No check on compressed bitstreams

One important limitation that most certainly will *not* be addressed in
any upcoming versions is that *jpylyzer* does not analyse the data in
the compressed bitstream segments. Doing so would involve decoding the
whole image, and this is completely out of *jpylyzer*�s scope. As a
result, it is possible that a JP2 that passes each of *jpylyzer*�s tests
will nevertheless fail to render correctly in a viewer application.

### Recommendations for use in quality assurance workflows

Because of the foregoing, a thorough JP2 quality assurance workflow
should not rely on *jpylyzer* (or any other format validator) alone, but
it should include other tests as well. Some obvious examples are:

�         A rendering test that checks if a file renders at all

�         Format migration workflows (e.g. TIFF to JP2) should ideally
also include some comparison between source and destination images (e.g.
a pixel-wise comparison)

Conversely, an image that successfully passes a rendering test or
pixel-wise comparison may still contain problematic features (e.g.
incorrect colour space information), so validation, rendering tests and
pixel-wise comparisons are really complementary to each other.

### Note on ICC profile support

At the time of writing an amendment is in preparation that will extend
the support for embedded ICC profiles in JP2. *Jpylyzer* is already
anticipating these changes, and as a result there is a minor discrepancy
here between *jpylyzer* and the current standard text.

1.3         Outline of this User Manual
---------------------------------------

Chapter 2 describes the installation process of *jpylyzer* for Windows
and Unix-based systems. Chapter 3 explains the usage of *jpylyzer* as a
command-line tool, or as an importable Python module. Chapter 4 gives a
brief overview of the structure of JP2 and its �box� structure.
*Jpylyzer*�s output format is explained in chapter 5. The final chapters
give a detailed description of the tests that *jpylyzer* performs for
validation, and its reported properties. Chapter 6 does this for all
�boxes�, except for the �Contiguous Codestream� box, which is given a
chapter (7) of its own.

1.4         Funding
-------------------

The development of *jpylyzer* was funded by the EU FP 7 project SCAPE
(SCAlabable Preservation Environments). More information about this
project can be found here:

[http://www.scape-project.eu/](http://www.scape-project.eu/)

1.5         License
-------------------

*Jpylyzer*is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version. This program is distributed in the hope
that it will be useful, but WITHOUT ANY WARRANTY; without even the
implied warranty of�� MERCHANTABILITY or FITNESS FOR A PARTICULAR
PURPOSE.� See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License
along with this program.� If not, see
\<[http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)\>.

On Debian systems, the complete text of the GNU Lesser General Public
License version 3 can be found in "/usr/share/common-licenses/LGPL-3".

 

**  
**

2               Installation and set-up
=======================================

2.1         Obtaining the software
----------------------------------

To obtain the latest version of the software please use the download
links at the *jpylyzer* homepage:

[http://openplanets.github.io/jpylyzer/](http://openplanets.github.io/jpylyzer/)

You have three options:

1.       Use the Python source code. This allows you to run the software
as a Python script on most popular platforms (Windows, Linux, Mac,
etc.). However, this requires that you have a recent version of the
Python interpreter available on your system.

2.       Alternatively, for Windows users there is also a set of
stand-alone binaries[[1]](#_ftn1). These allow you to run *jpylyzer* as
an executable Windows application, without any need for installing
Python. This option is particularly useful for Windows users who cannot
(or don�t want to) install software on their system.

3.       For Linux users Debian packages are available. These allow you
to run *jpylyzer* without any need for installing Python.

These options are described in the following sections.

2.2         Installation of Python script (Linux/Unix, Windows, Mac OS X)
-------------------------------------------------------------------------

First, download the source files using one of the �Source Code
Downloads� links on the OPF *jpylyzer* page.

Then unzip the contents of the ZIP file to an empty directory. If you
are working on a Linux/Unix based system you may need to make the
scripts executable, and convert any line breaks to Unix-style ones. To
do this, use the following commands:

chmod 755 \*.py

dos2unix \*.py

In order to run the script you will need either Python 2.7, or Python
3.2 (or more recent)[[2]](#_ftn2). Python can be downloaded from:

[http://python.org/](http://python.org/)

### Testing the installation

To test your installation, open a console window (or command prompt) and
type:

%jpylyzerPath%/jpylyzer.py -h

In the above command, replace %jpylyzerPath% with the full path to the
*jpylyzer* installation directory (i.e. the directory that contains
�jpylyzer.py� and its associated files). For example, if you extracted
the files to directory �/home/jpylyzer�, the command would become:

/home/jpylyzer/jpylyzer.py -h

Executing this command should result in the following screen output:

usage: jpylyzer.py [-h] [--verbose] [--wrapper] [--version] ...

 

JP2 image validator and properties extractor

 

positional arguments:

� jp2In��������� input JP2 image(s) or folder(s), prefix wildcard

���������������� (\*) with backslash (\\) in Linux

 

optional arguments:

� -h, --help���� show this help message and exit

� --verbose����� report test results in verbose format

� --wrapper, -w� wraps the output for individual image(s)

���������������� in'results' XML element

��--nullxml����� extract null-terminated XML content from XML and

���������������� UUID boxes (doesn't affect validation)���������������

� --version����� show program's version number and exit

### Troubleshooting

If the above test didn�t run successfully, first verify the following
possible causes:

�         On Windows: check if files with a *.py* extension are
associated with the Python interpreter. If you have multiple versions of
Python on your system, make sure that the association does not link to a
Python version that is incompatible with *jpylyzer* (e.g. Python 2.6 or
older, or Python 3.0/3.1).

�         On Unix/Linux: by default, *jpylyzer* uses the command
interpreter that is defined by the �python� environment variable. If
this is linked to some (very) old version of Python, things may not work
as expected. If you run into problems because of this, update the
command interpreter references in� *jpylyzer.py*, i.e. change:

\#! /usr/bin/env python

into:

\#! /usr/bin/env python27

2.3         Installation of Windows binaries (Windows only)
-----------------------------------------------------------

Download the binary using the link on the *jpylyzer* homepage. Unzip the
contents of this file to an empty folder on your PC.� *Jpylyzer* should
now be ready for use.

### Testing the installation

To test your installation, open a Command Prompt (�DOS prompt�) and
type:

%jpylyzerPath%\\jpylyzer -h

In the above command, replace %jpylyzerPath% with the full path to the
*jpylyzer* installation directory (i.e. the directory that contains
�jpylyzer.exe� and its associated files). For example, if you extracted
the files to directory �c:\\tools\\jpylyzer�, the command would become:

c:\\tools\\jpylyzer\\jpylyzer -h

Executing this command should result in the following screen output:

usage: jpylyzer.py [-h] [--verbose] [--wrapper] [--version] ...

 

JP2 image validator and properties extractor

 

positional arguments:

� jp2In��������� input JP2 image(s) or folder(s), prefix wildcard

���������������� (\*) with backslash (\\) in Linux

 

optional arguments:

� -h, --help���� show this help message and exit

� --verbose����� report test results in verbose format

� --wrapper, -w� wraps the output for individual image(s) in

���������������� 'results' XML element

� --nullxml����� extract null-terminated XML content from XML and

���������������� UUID boxes (doesn't affect validation)���������������

� --version����� show program's version number and exit

### Running jpylyzer without typing the full path

Optionally, you may also want to add the full path of the *jpylyzer*
installation directory to the Windows �Path� environment variable. Doing
so allows you to run *jpylyzer* from any directory on your PC without
having to type the full path. In Windows XP you can do this by selecting
�settings� from the �Start� menu; then go to �control panel�/�system�
and go to the �advanced� tab. Click on the �environment variables�
button. Finally, locate the �Path� variable in the �system variables�
window, click on �Edit� and add the full *jpylyzer* path (this requires
local Administrator privileges). The settings take effect on any newly
opened command prompt.

2.4         Installation of Debian packages (Ubuntu/Linux)
----------------------------------------------------------

For a number of Linux architectures Debian packages of *jpylyzer* exist.
To install, simply download the *.deb* file, double-click on it and
select *Install Package*.� Alternatively you can also do this in the
command terminal by typing:

sudo dpkg -i jpylyzer\_1.9.0\_i386.deb

In both cases you need to have administrative privileges.

**  
   
**

3               Using *jpylyzer*
================================

3.1         Overview
--------------------

This chapter describes the general use of *jpylyzer*. The first sections
cover the use of *jpylyzer* as a command-line tool and as an importable
Python module.

3.2         Command-line usage
------------------------------

This section explains *jpylyzer*�s general command-line interface. For
the sake of brevity, all command-line examples assume the use of the
Python script; moreover, full paths are omitted. This means that,
depending on your system and settings, you may have to substitute each
occurrence of �jpylyzer.py� with its full path, the corresponding
Windows binary, or a combination of both. The following examples
illustrate this:

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>This User Manual</p></td>
<td align="left"><p>jpylyzer.py</p></td>
</tr>
<tr class="even">
<td align="left"><p>Substitution example Linux</p></td>
<td align="left"><p>/home/jpylyzer/jpylyzer.py</p></td>
</tr>
<tr class="odd">
<td align="left"><p>Substitution example Windows binaries</p></td>
<td align="left"><p>c:\tools\jpylyzer\jpylyzer</p></td>
</tr>
</tbody>
</table>

 

Furthermore, command line arguments that are given between square
brackets (example: [-h]) are optional.

### Synopsis

*Jpylyzer*can be invoked using the following command-line arguments:

jpylyzer.py [-h] [--verbose] [--wrapper] [--version]

[--nullxml] [--nopretty] ...

With:

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>�</p></td>
<td align="left"><p>: input JP2 image(s)</p></td>
</tr>
<tr class="even">
<td align="left"><p>[-h, --help]</p></td>
<td align="left"><p>: show help message and exit</p></td>
</tr>
<tr class="odd">
<td align="left"><p>[--verbose]</p></td>
<td align="left"><p>: report test results in verbose format</p></td>
</tr>
<tr class="even">
<td align="left"><p>[--wrapper, -w]</p></td>
<td align="left"><p>: wraps the output for individual image(s) in 'results' XML element</p></td>
</tr>
<tr class="odd">
<td align="left"><p>[--nullxml]</p></td>
<td align="left"><p>: extract null-terminated XML content from XML and UUID boxes(doesn't affect validation)</p></td>
</tr>
<tr class="even">
<td align="left"><p>[--nopretty]</p></td>
<td align="left"><p>: suppress pretty-printing of XML output</p></td>
</tr>
<tr class="odd">
<td align="left"><p>[-v, --version]</p></td>
<td align="left"><p>: show program's version number and exit</p></td>
</tr>
</tbody>
</table>

 

Note that the input can either be a single image, a space-separated
sequence of images, a pathname expression that includes multiple images,
or any combination of the above. For example, the following command will
process one single image:

jpylyzer.py rubbish.jp2

The next example shows how to process all files with a �jp2� extension
in the current directory:

jpylyzer.py \*.jp2

Note that on Unix/Linux based systems pathname expressions may not work
properly unless you wrap them in quotation marks:

jpylyzer.py �\*.jp2�

### Output redirection

All output (except warning and system error messages) is directed to the
standard output device (stdout).� By default this is the console screen.
Use your platform�s standard output redirection operators to redirect
output to a file. The most common situation will be to redirect the
output of one invocation of *jpylyzer* to an XML file, which can be done
with the �\>� operator (both under Windows and Linux):

jpylyzer.py jp2In \> outputFile

E.g. the following command will run*jpylyzer* on image �rubbish.jp2� and
redirects the output to file �rubbish.xml�:

jpylyzer.py rubbish.jp2 \> rubbish.xml

The format of the XML output is described in Chapter 5.

### Creating well-formed XML with multiple images

By default, *jpylyzer* creates a separate XML tree for each analysed
image, without any �overarching hierarchy. If you use a pathname
expression to process multiple images and redirect the output to a file,
the resulting file will **not** be a well-formed XML document. An
example:

jpylyzer.py rubbish.jp2 garbage.jp2 \> rubbish.xml

In this case, the output for these 2 images is redirected to
�rubbish.xml�, but the file will be a succession of two XML trees, which
by itself is not well-formed XML.� Use the *--wrapper* option if you
want to create well-formed XML instead:

jpylyzer.py --wrapper rubbish.jp2 garbage.jp2 \> rubbish.xml

In the above case the XML trees of the individual images are wrapped
inside a �results� element.

### �nullxml� option

The *nullxml* option was added to enable extraction of XML content that
is terminated by a null-byte. By default *jpylyzer* doesn�t report the
XML in that case, because it throws an exception in the XML parser.
Apparently some old versions of the Kakadu demo applications would
erroneously add a null-byte to embedded XML, so this option can be used
to force extraction for images that are affected by this.

### User warnings

Under the following conditions *jpylyzer* will print a user warning to
the standard error device (typically the console screen):

1.       If there are no input images to check (typically because the
value of jp2In refers to a non-existent file), the� following� warning
message is shown:

User warning: no images to check!

2.       In some cases you will see the following warning message:

User warning: ignoring 'boxName' (validator function not yet
implemented)

The reason for this: a JP2 file is made up of units that are called
�boxes�. This is explained in more detail in Chapter 4. Each �box� has
its own dedicated validator function. At this stage validator functions
are still missing for a small number of (optional) boxes. *Jpylyzer*
will display the above warning message if it encounters a (yet)
unsupported box. Any unsupported boxes are simply ignored, and the
remainder of the file will be analyzed (and validated) normally.

3.       Finally, you may occasionally see this warning message:

User warning: ignoring unknown box

This happens if *jpylyzer* encounters a box that is not defined by JPEG
2000 Part 1. It should be noted that, to a large extent, JPEG 2000 Part
1 permits the presence of boxes that are defined outside the standard.
Again, *jpylyzer* will simply ignore these and process all other boxes
normally.

3.3         Using *jpylyzer* as a Python module
-----------------------------------------------

Instead of using *jpylyzer* from the command-line, you can also import
it as a module in your own Python programs. To do so, put all the
*jpylyzer* source files in the same directory as your own code. Then
import *jpylyzer* into your code by adding:

import jpylyzer

Subsequently you can call any function that is defined in *jpylyzer.py*.
In practice you will most likely only need the *checkOneFile* function,
which can be called in the following way:

jpylyzer.checkOneFile(file)

Here, *file* is the path to a file object. The function returns an
element object that can either be used directly, or converted to XML
using the *ElementTree* module[[3]](#_ftn3). The structure of the
element object follows the XML output that described in Chapter 5.

Alternatively, you may only want to import the *checkOneFile* function,
in which case the import statement becomes:

from jpylyzer import checkOneFile

This will allow you to call the function as follows:

checkOneFile(file)

  

 

 

**  
**

4               Structure of a JP2 file
=======================================

4.1         Scope of this chapter
---------------------------------

This chapter gives a brief overview of the JP2 file format. A basic
understanding of the general structure of JP2 is helpful for
appreciating how *jpylyzer* performs its validation. It will also make
it easier to understand *jpylyzer*�s extracted properties, as these are
reported as a hierarchical tree that corresponds to the internal
structure of JP2.

For an exhaustive description of every detail of the format you are
advised to consult Annex I (�JP2 file format syntax�) and Annex A
(�Codestream syntax�) of ISO/IEC 15444-1.

4.2         General format structure
------------------------------------

At the highest level, a JP2 file is made up of a collection of *boxes*.
A *box* can be thought of as the fundamental building block of the
format. Some boxes (�superboxes�) are containers for other boxes. Figure
4‑1 gives an overview of the top-level boxes in a JP2 file.

![](jpylyzerUserManual_files/image004.gif)

Figure 4‑1� Top-level overview of a JP2 file (based on Figure I.1 in
ISO/IEC 15444-1). Boxes with dashed borders are optional. 'Superbox'
denotes a box that contains other box(es).

 

A number of things here are noteworthy to point out:

�         Some of these boxes are required, whereas others (indicated
with dashed lines in Figure 4‑1) are optional.

�         The order in which the boxes appear in the file is subject to
some constraints (e.g. the first box in a JP2 must always be a
�Signature� box, followed by a �File Type� box).

�         �Some boxes may have multiple instances (e.g. �Contiguous
Codestream� box), whereas others must be unique (e.g.� �JP2 Header�
box).

More specific details can be found in the standard. The important thing
here is that requirements like the above are something that should be
verified by a validator, and this is exactly what *jpylyzer* does at the
highest level of its validation procedure.

4.3         General structure of a box
--------------------------------------

All boxes are defined by a generic binary structure, which is
illustrated by Figure 4‑2. Most boxes are made up of the following three
components:

1.       A fixed-length �box length� field that indicates the total size
of the box (in bytes).

2.       A fixed-length �box type� field which specifies the type of
information that can be found in this box

3.       The box contents, which contains the actual information within
the box. Its internal format depends on the box type. The box contents
of a �superbox� will contain its child boxes (which can be parsed
recursively).

In some cases a box will also contain an �extended box length field�.
This field is needed if the size of a box exceeds 2<sup>32</sup>-1
bytes, which is the maximum value that can be stored in the 4-byte �box
length� field.

![](jpylyzerUserManual_files/image005.jpg)

Figure 4‑2 General structure of a box (based on Figure I.4 in ISO/IEC
15444-1).

4.4         Defined boxes in JP2
--------------------------------

Table 4‑1 lists all boxes that are defined in ISO/IEC 15444-1. A JP2
file may contain boxes that are not defined by the standard. Such boxes
are simply skipped and ignored by conforming reader applications.�

  

 

Table 4‑1 Defined boxes in JP2 (taken from Table I.2 in ISO/IEC 15444-1,
with minor modifications). Indentation in �box name� column indicates
hierarchical structure.

<table>
<col width="25%" />
<col width="25%" />
<col width="25%" />
<col width="25%" />
<tbody>
<tr class="odd">
<td align="left"><p><strong>Box name</strong></p></td>
<td align="left"><p><strong>Superbox</strong></p></td>
<td align="left"><p><strong>Required?</strong></p></td>
<td align="left"><p><strong>Purpose</strong></p></td>
</tr>
<tr class="even">
<td align="left"><p>JPEG 2000 Signature box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Required</p></td>
<td align="left"><p>Identifies the file as being part of the JPEG 2000 family of files.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>File Type box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Required</p></td>
<td align="left"><p>Specifies file type, version and compatibility information, including specifying if this file is a conforming JP2 file or if it can be read by a conforming JP2 reader.</p></td>
</tr>
<tr class="even">
<td align="left"><p>JP2 Header box</p></td>
<td align="left"><p>Yes</p></td>
<td align="left"><p>Required</p></td>
<td align="left"><p>Contains a series of boxes that contain header-type information about the file.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>��������������� - Image Header box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Required</p></td>
<td align="left"><p>Specifies the size of the image and other related fields.</p></td>
</tr>
<tr class="even">
<td align="left"><p>��������������� - Bits Per Component box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies the bit depth of the components in the file in cases where the bit depth is not constant across all components.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>��������������� - Colour Specification box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Required</p></td>
<td align="left"><p>Specifies the colourspace of the image.</p></td>
</tr>
<tr class="even">
<td align="left"><p>��������������� - Palette box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies the palette which maps a single component in index space to a multiple-component image.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>��������������� - Component Mapping box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies the mapping between a palette and codestream components.</p></td>
</tr>
<tr class="even">
<td align="left"><p>��������������� - Channel Definition box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies the type and ordering of the components within the codestream, as well as those created by the application of a palette.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>��������������� - Resolution box</p></td>
<td align="left"><p>Yes</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Contains the grid resolution.</p></td>
</tr>
<tr class="even">
<td align="left"><p>������������������������������� - Capture</p>
<p>������������������������������� �� Resolution box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies the grid resolution at which the image was captured.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>������������������������������� - Default Display</p>
<p>������������������������������� �� Resolution box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies the default grid resolution at which the image should be displayed.</p></td>
</tr>
<tr class="even">
<td align="left"><p>Contiguous Codestream box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Required</p></td>
<td align="left"><p>Contains the codestream.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>Intellectual Property box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Contains intellectual property information about the image.</p></td>
</tr>
<tr class="even">
<td align="left"><p>XML box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Provides a tool by which vendors can add XML formatted information to a JP2 file.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>UUID box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Provides a tool by which vendors can add additional information to a file without risking conflict with other vendors.</p></td>
</tr>
<tr class="even">
<td align="left"><p>UUID Info box</p></td>
<td align="left"><p>Yes</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Provides a tool by which a vendor may provide access to additional information associated with a UUID.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>��������������� - UUID List box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies a list of UUIDs.</p></td>
</tr>
<tr class="even">
<td align="left"><p>��������������� - URL box</p></td>
<td align="left"><p>No</p></td>
<td align="left"><p>Optional</p></td>
<td align="left"><p>Specifies a URL.</p></td>
</tr>
</tbody>
</table>

 

  

 

**  
**

5               Output format
=============================

This chapter explains *jpylyzer*�s output format.

5.1         Overview
--------------------

*Jpylyzer*generates its output in XML format. Figure 5‑1 shows the
output structure.

![](jpylyzerUserManual_files/image006.gif)

Figure 5‑1 *Jpylyzer*�s XML output structure. Note that �box� elements
under �tests� and �properties� contain further sub-elements.

  

The root element (*jpylyzer*) contains 5 child elements:

1.       *toolInfo*: information about *jpylyzer*

2.       *fileInfo*: general information about the analysed file

3.       *isValidJP2*: outcome of the validation

4.       *tests*:� outcome of the individual tests that are part of the
validation process (organised by box)

5.       *properties*: image properties� (organised by box)

If *jpylyzer* is executed with the *--wrapper* option, the root element
is *results*, which contains one or more *jpylyzer* elements which
otherwise follow the above structure. From version 1.12 onward, the XML
output is pretty-printed. You can use the *--nopretty* switch to disable
pretty-printing (this produces smaller files and may give a slightly
better performance).

5.2         toolInfo element
----------------------------

This element holds information about *jpylyzer*. Currently it contains
the following sub-elements:

�         *toolName*: name of the analysis tool (i.e. *jpylyzer.py* or
*jpylyzer*, depending on whether the Python script or the Windows
binaries were used)

�         *toolVersion*: version of *jpylyzer* (*jpylyzer* uses a date
versioning scheme)

5.3         fileInfo element
----------------------------

This element holds general information about the analysed file.
Currently it contains the following sub-elements:

�         *filename*: name of the analysed file without its path (e.g.
�rubbish.jp2�)

�         *filePath*: name of the analysed file, including its full
absolute path (e.g. �d:\\data\\images\\rubbish.jp2�)

�         *fileSizeInBytes*: file size in bytes

�         *fileLastModified*: last modified date and time

5.4         isValidJP2 element
------------------------------

This element contains the results of the validation. If a file passed
all the tests (i.e. all tests returned �True�, see section 5.5) it is
most likely valid JP2, and the value of isValidJP2 will be �True�.� Its
value is �False� otherwise.

5.5         tests element
-------------------------

This element is reserved to hold the outcomes of all the individual
tests that *jpylyzer* performs to assess whether a file is valid JP2.
The results are organised in a hierarchical tree that corresponds to
JP2�s box structure. Each individual test can have two values:

�         �True� if a file passed the test.

�         �False� if a file failed the test.

If a file passed *all* tests, this is an indication that it is most
likely valid JP2. In that case, the *isValidJP2* element (section 5.4)
has a value of �True� (and �False� in all other cases). These tests are
all explained in chapters 6 and 7.

### Default and verbose reporting of test results

By default, *jpylyzer* only reports any tests that failed (i.e. returned
�False�), including the corresponding part of the box structure. For a
valid JP2 the tests element will be empty. �If the --verbose flag is
used, the results of *all* tests are included (including those that
returned �True�)[[4]](#_ftn4).

5.6         properties element
------------------------------

This element contains the extracted image properties, which are
organised in a hierarchical tree that corresponds to JP2�s box
structure. See chapters 6 and 7 for a description of the reported
properties.

**  
   
**

6               JP2: box by box
===============================

The following two chapters provide a detailed explanation of
*jpylyzer*�s functionality and its output. In particular, the following
two aspects are addressed:

1.       The reported properties

2.       The tests that *jpylyzer* performs to establish the validity of
a file.

6.1         About the properties and tests trees
------------------------------------------------

The �properties� element in *jpylyzer*�s output holds a hierarchical
tree structure that contains all extracted properties. The �tests� tree
follows the same structure. The hierarchy reflects JP2�s box structure
(explained in Chapter 4): each box is represented by a corresponding
output element that contains the corresponding property entries. If a
box is a superbox, the output element will contain child elements for
each child box. For some boxes, the output contains further
sub-elements. This applies in particular to the Contiguous Codestream
box, since its contents are more complex than any of the other boxes.
Also, if a Colour Specification box contains an embedded ICC profile,
the properties of the ICC profile are stored in a separate sub-element.
In addition to this, one �property� that is reported by *jpylyzer* (the
compression ratio) is not actually extracted from any particular box.
Instead, it is calculated from the file size and some properties from
the Header boxes. As a result, it is reported separately in the root of
the properties tree.

### Naming of properties

The naming of the reported properties largely follows the standard
(ISO/IEC 15444-1). Some minor differences follow from the fact that the
standard does have any consistent use of text case, whereas *jpylyzer*
uses lower camel case. In addition, some parameters in the standard are
compound units that aggregate a number of Boolean �switches�, where no
names are provided for each individual switch. An example of this is the
*Scod* (coding style) parameter in the codestream header, which contains
three switches that define the use of precincts, start-of-packet markers
and end-of-packet markers. For cases like these *jpylyzer* uses its own
(largely self-descriptive) names (which are all documented in these
chapters).

6.2         JPEG 2000 Signature box
-----------------------------------

This box contains information that allows identification of the file as
being part of the JPEG 2000 family of file formats.

### Element name

signatureBox

### Reported properties

None (box only holds JPEG 2000 signature, which includes non-printable
characters)

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>Size of box contents equals 4 bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>signatureIsValid</p></td>
<td align="left"><p>Signature equals 0x0d0a870a</p></td>
</tr>
</tbody>
</table>

6.3         File Type box
-------------------------

This box specifies file type, version and compatibility information,
including specifying if this file is a conforming JP2 file or if it can
be read by a conforming JP2 reader.

### Element name

fileTypeBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>br</p></td>
<td align="left"><p>Brand</p></td>
</tr>
<tr class="odd">
<td align="left"><p>minV</p></td>
<td align="left"><p>Minor version</p></td>
</tr>
<tr class="even">
<td align="left"><p>cL<sup>*</sup></p></td>
<td align="left"><p>Compatibility field (repeatable)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>(Size of box � 8) /4 is� a whole number (integer)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>brandIsValid</p></td>
<td align="left"><p><em>br</em> equals 0x6a703220 (�jp2 �)</p></td>
</tr>
<tr class="even">
<td align="left"><p>minorVersionIsValid</p></td>
<td align="left"><p><em>minV</em> equals 0</p></td>
</tr>
<tr class="odd">
<td align="left"><p>compatibilityListIsValid</p></td>
<td align="left"><p>Sequence of compatibility (<em>cL</em>) fields includes one entry that equals 0x6a703220 (�jp2 �)</p></td>
</tr>
</tbody>
</table>

6.4         JP2 Header box (superbox)
-------------------------------------

This box is a superbox that holds a series of boxes that contain
header-type information about the file.

### Element name

jp2HeaderBox

### Reported properties

Since this is a superbox, it contains a number of child boxes. These are
represented as child elements in the properties tree:

  

 

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Child element</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>imageHeaderBox (section 6.5)</p></td>
<td align="left"><p>Properties from Image Header box� (required)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>bitsPerComponentBox (section 6.6)</p></td>
<td align="left"><p>Properties from Bits Per Component box (optional)</p></td>
</tr>
<tr class="even">
<td align="left"><p>ColourSpecificationBox (section 6.7)</p></td>
<td align="left"><p>Properties from Colour Specification box (required)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>paletteBox (section 6.8)</p></td>
<td align="left"><p>Properties from Palette box (optional)</p></td>
</tr>
<tr class="even">
<td align="left"><p>componentMappingBox (section 6.9)</p></td>
<td align="left"><p>Properties from Component Mapping box (optional)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>channelDefinitionBox (section 6.10)</p></td>
<td align="left"><p>Properties from Channel Definition box (optional)</p></td>
</tr>
<tr class="even">
<td align="left"><p>resolutionBox (section 6.11)</p></td>
<td align="left"><p>Properties from Resolution box (optional)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsImageHeaderBox</p></td>
<td align="left"><p>Box contains required Image Header box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>containsColourSpecificationBox</p></td>
<td align="left"><p>Box contains required Colour Specification box</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsBitsPerComponentBox</p></td>
<td align="left"><p>Box contains Bits Per Component Box, which is required if <em>bPCSign</em> and <em>bPCDepth</em> in Image Header Box equal 1 and 128, respectively (test is skipped otherwise)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>firstJP2HeaderBoxIsImageHeaderBox</p></td>
<td align="left"><p>First child box is Image Header Box</p></td>
</tr>
<tr class="even">
<td align="left"><p>noMoreThanOneImageHeaderBox</p></td>
<td align="left"><p>Box contains no more than one Image Header box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>noMoreThanOneBitsPerComponentBox</p></td>
<td align="left"><p>Box contains no more than one Bits Per Component box</p></td>
</tr>
<tr class="even">
<td align="left"><p>noMoreThanOnePaletteBox</p></td>
<td align="left"><p>Box contains no more than one Palette box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>noMoreThanOneComponentMappingBox</p></td>
<td align="left"><p>Box contains no more than one Component Mapping box</p></td>
</tr>
<tr class="even">
<td align="left"><p>noMoreThanOneChannelDefinitionBox</p></td>
<td align="left"><p>Box contains no more than one Channel Definition box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>noMoreThanOneResolutionBox</p></td>
<td align="left"><p>Box contains no more than one Resolution box</p></td>
</tr>
<tr class="even">
<td align="left"><p>colourSpecificationBoxesAreContiguous</p></td>
<td align="left"><p>In case of multiple Colour Specification boxes, they appear contiguously in the JP2 Header box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>paletteAndComponentMappingBoxes</p>
<p>OnlyTogether</p></td>
<td align="left"><p>Box contains a Palette box (only if Component Mapping box is present); box contains a Component Mapping box (only if Palette box is present)</p></td>
</tr>
</tbody>
</table>

 

6.5         Image Header box (child of JP2 Header box)
------------------------------------------------------

This box specifies the size of the image and other related fields.

### Element name

imageHeaderBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>height</p></td>
<td align="left"><p>Image height in pixels</p></td>
</tr>
<tr class="odd">
<td align="left"><p>width</p></td>
<td align="left"><p>Image width in pixels</p></td>
</tr>
<tr class="even">
<td align="left"><p>nC</p></td>
<td align="left"><p>Number of image components</p></td>
</tr>
<tr class="odd">
<td align="left"><p>bPCSign</p></td>
<td align="left"><p>Indicates whether image components are signed or unsigned</p></td>
</tr>
<tr class="even">
<td align="left"><p>bPCDepth</p></td>
<td align="left"><p>Number of bits per component</p></td>
</tr>
<tr class="odd">
<td align="left"><p>c</p></td>
<td align="left"><p>Compression type</p></td>
</tr>
<tr class="even">
<td align="left"><p>unkC</p></td>
<td align="left"><p>Colourspace Unknown field (�yes� if colourspace of image data is unknown; �no� otherwise)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>iPR</p></td>
<td align="left"><p>Intellectual Property field (�yes� if� image contains intellectual property rights information; �no� otherwise)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>Size of box contents equals 14 bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>heightIsValid</p></td>
<td align="left"><p><em>height</em> is within range [1, 2<sup>32</sup> - 1]</p></td>
</tr>
<tr class="even">
<td align="left"><p>widthIsValid</p></td>
<td align="left"><p><em>width</em> is within range [1, 2<sup>32</sup> - 1]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>nCIsValid</p></td>
<td align="left"><p><em>nC</em> is within range [1, 16384]</p></td>
</tr>
<tr class="even">
<td align="left"><p>bPCIsValid</p></td>
<td align="left"><p><em>bPCDepth</em> is within range [1,38] OR <em>bPCSign</em> equals 255 (in the latter case the bit depth is variable)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>cIsValid</p></td>
<td align="left"><p><em>c</em> equals 7 (�jpeg2000�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>unkCIsValid</p></td>
<td align="left"><p><em>unkC</em> equals 0 (�no�) or 1 (�yes�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>iPRIsValid</p></td>
<td align="left"><p><em>iPR</em> equals� 0 (�no�) or 1 (�yes�)</p></td>
</tr>
</tbody>
</table>

 

6.6         Bits Per Component box (child of JP2 Header box)
------------------------------------------------------------

This (optional) box specifies the bit depth of the components in the
file in cases where the bit depth is not constant across all components.

### Element name

bitsPerComponentBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>bPCSign<sup>*</sup></p></td>
<td align="left"><p>Indicates whether image component is signed or unsigned (repeated for each component)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>bPCDepth<sup>*</sup></p></td>
<td align="left"><p>Number of bits for this component� (repeated for each component)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>bPCIsValid<sup>*</sup></p></td>
<td align="left"><p><em>bPCDepth</em> is within range [1,38] �(repeated for each component)</p></td>
</tr>
</tbody>
</table>

 

6.7         Colour Specification box (child of JP2 Header box)
--------------------------------------------------------------

This box specifies the colourspace of the image.

### Element name

colourSpecificationBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>meth</p></td>
<td align="left"><p>Specification method. Indicates whether colourspace of this image is defined as an enumerated colourspace or using a (restricted) ICC profile.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>prec</p></td>
<td align="left"><p>Precedence</p></td>
</tr>
<tr class="even">
<td align="left"><p>approx</p></td>
<td align="left"><p>Colourspace approximation</p></td>
</tr>
<tr class="odd">
<td align="left"><p>enumCS (if meth equals �Enumerated�)</p></td>
<td align="left"><p>Enumerated colourspace (as descriptive text string)</p></td>
</tr>
<tr class="even">
<td align="left"><p>icc� (if meth equals �Restricted ICC� or �Any ICC�<a href="#_ftn5">[5]</a>)</p></td>
<td align="left"><p>Properties of ICC profile as child element (see below)</p></td>
</tr>
</tbody>
</table>

### Reported properties of ICC profiles

If the colour specification box contains an embedded ICC profile,
*jpylyzer* will also report the following properties (which are all
grouped in an �icc� sub-element in the properties tree). An exhaustive
explanation of these properties is given in the ICC specification (ISO
15076-1 / ICC.1:2004-10). Note that *jpylyzer* does *not* validate
embedded ICC profiles (even though it does check if a specific ICC
profile is allowed in JP2)!

  

 

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>profileSize</p></td>
<td align="left"><p>Size of ICC profile in bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>preferredCMMType</p></td>
<td align="left"><p>Preferred CMM type</p></td>
</tr>
<tr class="even">
<td align="left"><p>profileVersion</p></td>
<td align="left"><p>Profile version. Format: �majorRevision.minorRevision.bugFixRevision�</p></td>
</tr>
<tr class="odd">
<td align="left"><p>profileClass</p></td>
<td align="left"><p>Profile/device class</p></td>
</tr>
<tr class="even">
<td align="left"><p>colourSpace</p></td>
<td align="left"><p>Colourspace</p></td>
</tr>
<tr class="odd">
<td align="left"><p>profileConnectionSpace</p></td>
<td align="left"><p>Profile connection space</p></td>
</tr>
<tr class="even">
<td align="left"><p>dateTimeString</p></td>
<td align="left"><p>Date / time string. Format: �YYYY/MM/DD, h:m:s�</p></td>
</tr>
<tr class="odd">
<td align="left"><p>profileSignature</p></td>
<td align="left"><p>Profile signature</p></td>
</tr>
<tr class="even">
<td align="left"><p>primaryPlatform</p></td>
<td align="left"><p>Primary platform</p></td>
</tr>
<tr class="odd">
<td align="left"><p>embeddedProfile</p></td>
<td align="left"><p>Flag that indicates whether profile is embedded in file (�yes�/�no�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>profileCannotBeUsedIndependently</p></td>
<td align="left"><p>Flag that indicates whether profile can<em>not</em> (!) be used independently from the embedded colour data (�yes�/�no�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>deviceManufacturer</p></td>
<td align="left"><p>Identifies a device manufacturer</p></td>
</tr>
<tr class="even">
<td align="left"><p>deviceModel</p></td>
<td align="left"><p>Identifies a device model</p></td>
</tr>
<tr class="odd">
<td align="left"><p>transparency</p></td>
<td align="left"><p>Indicates whether device medium is reflective or transparent</p></td>
</tr>
<tr class="even">
<td align="left"><p>glossiness</p></td>
<td align="left"><p>Indicates whether device medium is glossy or matte</p></td>
</tr>
<tr class="odd">
<td align="left"><p>polarity</p></td>
<td align="left"><p>Indicates whether device medium is positive or negative</p></td>
</tr>
<tr class="even">
<td align="left"><p>colour</p></td>
<td align="left"><p>Indicates whether device medium is colour or black and white</p></td>
</tr>
<tr class="odd">
<td align="left"><p>renderingIntent</p></td>
<td align="left"><p>Rendering intent</p></td>
</tr>
<tr class="even">
<td align="left"><p>connectionSpaceIlluminantX</p></td>
<td align="left"><p>Profile connection space illuminant X</p></td>
</tr>
<tr class="odd">
<td align="left"><p>connectionSpaceIlluminantY</p></td>
<td align="left"><p>Profile connection space illuminant Y</p></td>
</tr>
<tr class="even">
<td align="left"><p>connectionSpaceIlluminantZ</p></td>
<td align="left"><p>Profile connection space illuminant Z</p></td>
</tr>
<tr class="odd">
<td align="left"><p>profileCreator</p></td>
<td align="left"><p>Identifies� creator of profile</p></td>
</tr>
<tr class="even">
<td align="left"><p>profileID</p></td>
<td align="left"><p>Profile checksum (as hexadecimal string)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>tag<sup>*</sup></p></td>
<td align="left"><p>Signature of profile tag (repeated for each tag in the profile)</p></td>
</tr>
<tr class="even">
<td align="left"><p>description</p></td>
<td align="left"><p>Profile description (extracted from �desc� tag)</p></td>
</tr>
</tbody>
</table>

###  

**  
**

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>methIsValid</p></td>
<td align="left"><p><em>meth</em> equals 1 (enumerated colourspace) or 2 (restricted ICC profile)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>precIsValid</p></td>
<td align="left"><p><em>prec</em> equals 0</p></td>
</tr>
<tr class="even">
<td align="left"><p>approxIsValid</p></td>
<td align="left"><p><em>approx</em> equals 0</p></td>
</tr>
<tr class="odd">
<td align="left"><p>enumCSIsValid� (if meth equals �Enumerated�)</p></td>
<td align="left"><p><em>enumCS</em> equals 16 (�sRGB�), 17 (�greyscale�)� or 18 (�sYCC�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>iccSizeIsValid (if meth equals �Restricted ICC�)</p></td>
<td align="left"><p>Actual size of embedded ICC profile equals value of profileSize field in ICC header</p></td>
</tr>
<tr class="odd">
<td align="left"><p>iccPermittedProfileClass (if meth equals �Restricted ICC�)</p></td>
<td align="left"><p>ICC profile class is� �input device� or �display device�<a href="#_ftn6">[6]</a></p></td>
</tr>
<tr class="even">
<td align="left"><p>iccNoLUTBasedProfile (if meth equals �Restricted ICC�)</p></td>
<td align="left"><p>ICC profile type is not N-component LUT based (which is not allowed in JP2)</p></td>
</tr>
</tbody>
</table>

 

6.8         Palette box (child of JP2 Header box)
-------------------------------------------------

This (optional) box specifies the palette which maps a single component
in index space to a multiple-component image.

### Element name

paletteBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>nE</p></td>
<td align="left"><p>Number of entries in the table</p></td>
</tr>
<tr class="odd">
<td align="left"><p>nPC</p></td>
<td align="left"><p>Number of palette columns</p></td>
</tr>
<tr class="even">
<td align="left"><p>bSign<sup>*</sup></p></td>
<td align="left"><p>Indicates whether values created by this palette column are signed or unsigned (repeated for each column)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>bDepth<sup>*</sup></p></td>
<td align="left"><p>Bit depth of values created by this palette column (repeated for each column)</p></td>
</tr>
<tr class="even">
<td align="left"><p>cP<sup>**</sup></p></td>
<td align="left"><p>Value for this entry (repeated for each column, and for the number of entries)</p></td>
</tr>
</tbody>
</table>

###  

**  
**

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>nEIsValid</p></td>
<td align="left"><p><em>nE</em> is within range [0,1024]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>nPCIsValid</p></td>
<td align="left"><p><em>nPC</em> is within range [1,255]</p></td>
</tr>
<tr class="even">
<td align="left"><p>bDepthIsValid<sup>*</sup></p></td>
<td align="left"><p><em>bDepth</em> is within range [1,38]� (repeated for each column)</p></td>
</tr>
</tbody>
</table>

6.9         Component Mapping box (child of JP2 Header box)
-----------------------------------------------------------

This (optional) box specifies the mapping between a palette and
codestream components.

### Element name

componentMappingBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>cMP<sup>*</sup></p></td>
<td align="left"><p>Component index (repeated for each channel)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>mTyp<sup>*</sup></p></td>
<td align="left"><p>Specifies how channel is generated from codestream component (repeated for each channel)</p></td>
</tr>
<tr class="even">
<td align="left"><p>pCol<sup>*</sup></p></td>
<td align="left"><p>Palette component index (repeated for each channel)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>cMPIsValid</p></td>
<td align="left"><p><em>cMP</em> is within range [0,16384]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>mTypIsValid<sup>*</sup></p></td>
<td align="left"><p><em>mTyp</em> is within range [0,1] (repeated for each channel)</p></td>
</tr>
<tr class="even">
<td align="left"><p>pColIsValid<sup>*</sup></p></td>
<td align="left"><p><em>pCol</em> is 0 if �<em>mTyp</em> is 0� (repeated for each channel)</p></td>
</tr>
</tbody>
</table>

 

6.10     Channel Definition box (child of JP2 Header box)
---------------------------------------------------------

This (optional) box specifies the type and ordering of the components
within the codestream, as well as those created by the application of a
palette.

### Element name

channelDefinitionBox

**  
**

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>n</p></td>
<td align="left"><p>Number of channel descriptions</p></td>
</tr>
<tr class="odd">
<td align="left"><p>cN<sup>*</sup></p></td>
<td align="left"><p>Channel index (repeated for each channel)</p></td>
</tr>
<tr class="even">
<td align="left"><p>cTyp<sup>*</sup></p></td>
<td align="left"><p>Channel type (repeated for each channel)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>cAssoc<sup>*</sup></p></td>
<td align="left"><p>Channel association� (repeated for each channel)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>nIsValid</p></td>
<td align="left"><p><em>n</em> is within range [1, 65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>(Size of box � 2) / equals 6*<em>n</em></p></td>
</tr>
<tr class="even">
<td align="left"><p>cNIsValid<sup>*</sup></p></td>
<td align="left"><p><em>cN</em> is within range [0, 65535] (repeated for each channel)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>cTypIsValid<sup>*</sup></p></td>
<td align="left"><p><em>cType</em> is within range [0, 65535] (repeated for each channel)</p></td>
</tr>
<tr class="even">
<td align="left"><p>cAssocIsValid<sup>*</sup></p></td>
<td align="left"><p><em>cAssoc</em> is within range [0, 65535] (repeated for each channel)</p></td>
</tr>
</tbody>
</table>

 

6.11     Resolution box (child of JP2 Header box, superbox)
-----------------------------------------------------------

This (optional) box contains the grid resolution.

### Element name

resolutionBox

### Reported properties

Since this is a superbox, it contains one or two child boxes. These are
represented as child elements in the properties tree:

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Child element</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>captureResolutionBox (section 6.12)</p></td>
<td align="left"><p>Properties from Capture Resolution box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>displayResolutionBox (section 6.13)</p></td>
<td align="left"><p>Properties from Default Display Resolution box</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsCaptureOrDisplayResolutionBox</p></td>
<td align="left"><p>Box contains either a Capture Resolution box or a Default Display Resolution box, or both</p></td>
</tr>
<tr class="odd">
<td align="left"><p>noMoreThanOneCaptureResolutionBox</p></td>
<td align="left"><p>Box contains no more than one Capture Resolution box</p></td>
</tr>
<tr class="even">
<td align="left"><p>noMoreThanOneDisplayResolutionBox</p></td>
<td align="left"><p>Box contains no more than one Default Display Resolution box</p></td>
</tr>
</tbody>
</table>

6.12     Capture Resolution box (child of Resolution box)
---------------------------------------------------------

This (optional) box specifies the grid resolution at which the image was
captured.

### Element name

captureResolutionBox

### Reported properties

Resolution information in this box is stored as a set of vertical and
horizontal numerators, denominators and exponents. *Jpylyzer* also
reports the corresponding grid resolutions in pixels per meter and
pixels per inch, which are calculated from these values.

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRcN</p></td>
<td align="left"><p>Vertical grid resolution numerator</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vRcD</p></td>
<td align="left"><p>Vertical grid resolution denominator</p></td>
</tr>
<tr class="even">
<td align="left"><p>hRcN</p></td>
<td align="left"><p>Horizontal grid resolution numerator</p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRcD</p></td>
<td align="left"><p>Horizontal grid resolution denominator</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRcE</p></td>
<td align="left"><p>Vertical grid resolution exponent</p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRcE</p></td>
<td align="left"><p>Horizontal grid resolution exponent</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRescInPixelsPerMeter</p></td>
<td align="left"><p>Vertical grid resolution, expressed in pixels per meter<a href="#_ftn7">[7]</a></p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRescInPixelsPerMeter</p></td>
<td align="left"><p>Horizontal grid resolution, expressed in pixels per meter<a href="#_ftn8">[8]</a></p></td>
</tr>
<tr class="even">
<td align="left"><p>vRescInPixelsPerInch</p></td>
<td align="left"><p>Vertical grid resolution, expressed in pixels per inch<a href="#_ftn9">[9]</a></p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRescInPixelsPerInch</p></td>
<td align="left"><p>Horizontal grid resolution, expressed in pixels per inch<a href="#_ftn10">[10]</a></p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>Size of box contents equals 10 bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vRcNIsValid</p></td>
<td align="left"><p><em>vRcN</em> is within range [1,65535]</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRcDIsValid</p></td>
<td align="left"><p><em>vRcD</em> is within range [1,65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRcNIsValid</p></td>
<td align="left"><p><em>hRcN</em> is within range [1,65535]</p></td>
</tr>
<tr class="even">
<td align="left"><p>hRcDIsValid</p></td>
<td align="left"><p><em>hRcD</em> is within range [1,65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vRcEIsValid</p></td>
<td align="left"><p><em>vRcE</em> is within range [-127,128]</p></td>
</tr>
<tr class="even">
<td align="left"><p>hRcEIsValid</p></td>
<td align="left"><p><em>hRcE</em> is within range [-127,128]</p></td>
</tr>
</tbody>
</table>

6.13     Default Display Resolution box (child of Resolution box)
-----------------------------------------------------------------

This (optional) box specifies the default grid resolution at which the
image should be displayed.

### Element name

displayResolutionBox

### Reported properties

Resolution information in this box is stored as a set of vertical and
horizontal numerators, denominators and exponents. *Jpylyzer* also
reports the corresponding grid resolutions in pixels per meter and
pixels per inch, which are calculated from these values.

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRdN</p></td>
<td align="left"><p>Vertical grid resolution numerator</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vRdD</p></td>
<td align="left"><p>Vertical grid resolution denominator</p></td>
</tr>
<tr class="even">
<td align="left"><p>hRdN</p></td>
<td align="left"><p>Horizontal grid resolution numerator</p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRdD</p></td>
<td align="left"><p>Horizontal grid resolution denominator</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRdE</p></td>
<td align="left"><p>Vertical grid resolution exponent</p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRdE</p></td>
<td align="left"><p>Horizontal grid resolution exponent</p></td>
</tr>
<tr class="even">
<td align="left"><p>vResdInPixelsPerMeter</p></td>
<td align="left"><p>Vertical grid resolution, expressed in pixels per meter<a href="#_ftn11">[11]</a></p></td>
</tr>
<tr class="odd">
<td align="left"><p>hResdInPixelsPerMeter</p></td>
<td align="left"><p>Horizontal grid resolution, expressed in pixels per meter<a href="#_ftn12">[12]</a></p></td>
</tr>
<tr class="even">
<td align="left"><p>vResdInPixelsPerInch</p></td>
<td align="left"><p>Vertical grid resolution, expressed in pixels per inch<a href="#_ftn13">[13]</a></p></td>
</tr>
<tr class="odd">
<td align="left"><p>hResdInPixelsPerInch</p></td>
<td align="left"><p>Horizontal grid resolution, expressed in pixels per inch<a href="#_ftn14">[14]</a></p></td>
</tr>
</tbody>
</table>

###  

**  
**

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>Size of box contents equals 10 bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vRdNIsValid</p></td>
<td align="left"><p><em>vRdN</em> is within range [1,65535]</p></td>
</tr>
<tr class="even">
<td align="left"><p>vRdDIsValid</p></td>
<td align="left"><p><em>vRdD</em> is within range [1,65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>hRdNIsValid</p></td>
<td align="left"><p><em>hRdN</em> is within range [1,65535]</p></td>
</tr>
<tr class="even">
<td align="left"><p>hRdDIsValid</p></td>
<td align="left"><p><em>hRdD</em> is within range [1,65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vRdEIsValid</p></td>
<td align="left"><p><em>vRdE</em> is within range [-127,128]</p></td>
</tr>
<tr class="even">
<td align="left"><p>hRdEIsValid</p></td>
<td align="left"><p><em>hRdE</em> is within range [-127,128]</p></td>
</tr>
</tbody>
</table>

6.14     Contiguous Codestream box
----------------------------------

This box contains the codestream. See chapter 7.

6.15     Intellectual Property box
----------------------------------

This (optional) box contains intellectual property information about the
image. The JP2 format specification (ISO/IEC 15444-1) does not provide
any specific information about this box, other than stating that �the
definition of the format of [its] contents [�] is reserved for ISO�.� As
a result, *jpylyzer* does not currently include a validator function for
this box, which is now simply ignored. *Jpylyzer* will display a user
warning message in that case.

6.16     XML box
----------------

This (optional) box contains XML formatted information.

### Element name

xmlBox

### Reported properties

If the contents of this box are well-formed XML (see �tests� below), the
�xmlBox� element in the properties tree will contain the contents of the
XML box. Note that, depending on the character encoding of the original
XML, it may contain characters that are not allowed in the encoding that
is used for *jpylyzer*�s output. Any such characters will be represented
by numerical entity references in the output. If the box contents are
not well-formed XML, no properties are reported for this box.

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsWellformedXML</p></td>
<td align="left"><p>Contents of box are parsable, well-formed XML</p></td>
</tr>
</tbody>
</table>

 

Note that *jpylyzer* does not check whether the XML is *valid*, as this
is not required by the standard. Besides, doing so would make *jpylyzer*
significantly slower for XML that contains references to external
schemas and DTDs.

6.17     UUID box
-----------------

This (optional) box contains additional (binary) information, which may
be vendor-specific. Some applications (e.g. Kakadu and ExifTool) also
use this box for storing XMP metadata (see Section 1.1.4 in Part 3 of
the XMP specification[[15]](#_ftn15)).

### Element name

uuidBox

### Reported properties

If the value of *uuid* indicates the presence of XMP metadata and the
contents of this box are well-formed XML, (see �tests� below), the
�uuidBox� element in the properties tree will contain the XMP data. Note
that, depending on the character encoding of the original XML, it may
contain characters that are not allowed in the encoding that is used for
*jpylyzer*�s output. Any such characters will be represented by
numerical entity references in the output. In all other cases, the
�uuidBox� element will contain a standard string representation the of
UUID.

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>uuid</p></td>
<td align="left"><p>Standard string representation of UUID (<strong>only</strong> if uuid has value other than <em>be7acfcb-97a9-42e8-9c71-999491e3afac</em>). For an explanation of UUIDs see e.g. Leach <em>et al</em>., 2005.</p></td>
</tr>
<tr class="odd">
<td align="left"><p>XMP data</p></td>
<td align="left"><p>XMP metadata (<strong>only</strong> if uuid has value <em>be7acfcb-97a9-42e8-9c71-999491e3afac</em>)</p></td>
</tr>
</tbody>
</table>

 

Note that except for the XMP case, *jpylyzer* will not be able to report
any information on the actual contents of this box, since it is defined
outside of the scope of JPEG 2000.

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>Size of box contents is greater than 16 bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>containsWellformedXML</p></td>
<td align="left"><p>Contents of box are parsable, well-formed XML (this test is <strong>only</strong> performed if uuid has value <em>be7acfcb-97a9-42e8-9c71-999491e3afac</em>)</p></td>
</tr>
</tbody>
</table>

 

**  
**

6.18     UUID Info box (superbox)
---------------------------------

This (optional) box contains additional information associated with a
UUID.

### Element name

uuidInfoBox

### Reported properties

This is a superbox which contains two child boxes. These are represented
as child elements in the properties tree:

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Child element</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>uuidListBox (section 6.19)</p></td>
<td align="left"><p>Properties from UUID List box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>urlBox (section 6.20)</p></td>
<td align="left"><p>Properties from Data Entry URL box</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsOneListBox</p></td>
<td align="left"><p>Box contains exactly one UUID List box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>containsOneURLBox</p></td>
<td align="left"><p>Box contains exactly one Data Entry URL box</p></td>
</tr>
</tbody>
</table>

 

6.19     UUID List box (child of UUID Info box)
-----------------------------------------------

This (optional) box specifies a list of UUIDs.

### Element name

uuidListBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>nU</p></td>
<td align="left"><p>Number of UUIDs</p></td>
</tr>
<tr class="odd">
<td align="left"><p>uuid<sup>*</sup></p></td>
<td align="left"><p>Standard string representation of UUID� (repeated <em>nU</em> times)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxLengthIsValid</p></td>
<td align="left"><p>Size of box equals <em>nU</em>*16 + 2</p></td>
</tr>
</tbody>
</table>

 

6.20     Data Entry URL box (child of UUID Info box)
----------------------------------------------------

This (optional) box specifies a URL.

### Element name

urlBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>version</p></td>
<td align="left"><p>Version number</p></td>
</tr>
<tr class="odd">
<td align="left"><p>loc</p></td>
<td align="left"><p>Location, which specifies a URL of the additional information associated with the UUIDs in the UUID List box that resides in the same UUID Info box</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>flagIsValid</p></td>
<td align="left"><p>Three bytes that make up �flag� field equal 0x00 00 00 (�flag� is not reported to output because it only contains null bytes)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>locIsUTF8</p></td>
<td align="left"><p>Location (URL) can be decoded to UTF-8</p></td>
</tr>
<tr class="even">
<td align="left"><p>locHasNullTerminator</p></td>
<td align="left"><p>Location (URL) is a null-terminated string</p></td>
</tr>
</tbody>
</table>

 

6.21     Unknown box
--------------------

An image may contain boxes that are not defined by ISO/IEC 15444-1.
Although *jpylyzer* ignores such boxes, it will report some minimal info
that will allow interested users to identify them to a limited extent. �

### Element name

unknownBox

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>boxType</p></td>
<td align="left"><p>Four-character text string that specifies the type of information that is found in this box (corresponds to <em>TBox</em> in section I.4 of� ISO/IEC 15444-1).</p></td>
</tr>
</tbody>
</table>

 

6.22     Top-level tests and properties
---------------------------------------

This section describes the tests and output for the top file level.

### Element name

properties

### Reported properties

The metrics that are listed here are not �properties� in a strict sense;
instead they are secondary or derived metrics that are calculated by
combining information from different parts / boxes of the file.

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>compressionRatio</p></td>
<td align="left"><p>Compression ratio</p></td>
</tr>
</tbody>
</table>

 

The compression ratio is calculated as the ratio between the size of the
uncompressed image data and the actual file size:

![](jpylyzerUserManual_files/image007.gif)

�Here, *sizeCompressed* is simply the file size (*fileSizeInBytes* in
output file�s �fileInfo� element). The uncompressed size (in bytes) can
be calculated by multiplying the number of bytes per pixel by the total
number of pixels:

![](jpylyzerUserManual_files/image008.gif)�

With:

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>nC</p></td>
<td align="left"><p>: number of image components (from Image Header box)</p></td>
</tr>
<tr class="even">
<td align="left"><p>i</p></td>
<td align="left"><p>: component index</p></td>
</tr>
<tr class="odd">
<td align="left"><p>bPCDepth<sub>i</sub></p></td>
<td align="left"><p>: bits per component for component <em>i</em> (from Image Header box or Bits Per</p>
<p>��������������� Component box)</p></td>
</tr>
<tr class="even">
<td align="left"><p>height</p></td>
<td align="left"><p>: image height (from Image Header box)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>width</p></td>
<td align="left"><p>: image width (from Image Header box)</p></td>
</tr>
</tbody>
</table>

 

In addition, the root of the properties tree contains the elements for
all top-level boxes:

**  
**

 

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Child element</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>signatureBox (section 6.2)</p></td>
<td align="left"><p>Properties from JPEG 2000 Signature box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>fileTypeBox (section 6.3)</p></td>
<td align="left"><p>Properties from File Type box</p></td>
</tr>
<tr class="even">
<td align="left"><p>jp2HeaderBox (section 6.4)</p></td>
<td align="left"><p>Properties from JP2 Header box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>contiguousCodestreamBox (chapter 7)</p></td>
<td align="left"><p>Properties from Contiguous Codestream box</p></td>
</tr>
<tr class="even">
<td align="left"><p>intellectualPropertyBox (section 6.15)</p></td>
<td align="left"><p>Properties from Intellectual Property box (optional)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>xmlBox (section 6.16)</p></td>
<td align="left"><p>Properties from XML box (optional)</p></td>
</tr>
<tr class="even">
<td align="left"><p>uuidBox (section 6.17)</p></td>
<td align="left"><p>Properties from UUID box (optional)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>uuidInfoBox (section 6.18)</p></td>
<td align="left"><p>Properties from UUID Info box (optional)</p></td>
</tr>
</tbody>
</table>

 

### Tests

The tests that *jpylyzer* performs at the root level fall in either of
the following two categories:

1.       Tests for the presence of required top-level boxes, the order
in which they appear and restrictions on the number of instances for
specific boxes

2.       Tests for consistency of information in different parts of the
file. In particular, a lot of the information in the Image Header box is
redundant with information in the codestream header, and *jpylyzer*
performs a number of tests to verify the consistency between these
two.��

**  
**

 

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsSignatureBox</p></td>
<td align="left"><p>File root contains a JPEG 2000 Signature box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>containsFileTypeBox</p></td>
<td align="left"><p>File root contains a File Type box</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsJP2HeaderBox</p></td>
<td align="left"><p>File root contains a JP2 Header box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>containsContiguousCodestreamBox</p></td>
<td align="left"><p>File root contains a Contiguous Codestream box</p></td>
</tr>
<tr class="even">
<td align="left"><p>containsIntellectualPropertyBox</p></td>
<td align="left"><p>File root contains an Intellectual Property box, which is required if <em>iPR</em> field in Image Header Box equals 1 (test is skipped otherwise)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>firstBoxIsSignatureBox</p></td>
<td align="left"><p>First box is JPEG 2000 Signature box</p></td>
</tr>
<tr class="even">
<td align="left"><p>secondBoxIsFileTypeBox</p></td>
<td align="left"><p>Second box is File Type box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>locationJP2HeaderBoxIsValid</p></td>
<td align="left"><p>JP2 Header box is located after File Type Box and before (first) Contiguous Codestream box</p></td>
</tr>
<tr class="even">
<td align="left"><p>noMoreThanOneSignatureBox</p></td>
<td align="left"><p>File root contains no more than one JPEG 2000 Signature box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>noMoreThanOneFileTypeBox</p></td>
<td align="left"><p>File root contains no more than one File Type box</p></td>
</tr>
<tr class="even">
<td align="left"><p>noMoreThanOneJP2HeaderBox</p></td>
<td align="left"><p>File root contains no more than one JP2 Header box</p></td>
</tr>
<tr class="odd">
<td align="left"><p>heightConsistentWithSIZ</p></td>
<td align="left"><p>Value of <em>height</em> from Image Header Box equals <em>ysiz �yOsiz</em> from codestream SIZ header</p></td>
</tr>
<tr class="even">
<td align="left"><p>widthConsistentWithSIZ</p></td>
<td align="left"><p>Value of <em>width</em> from Image Header Box equals <em>xsiz</em> �<em>xOsiz</em> from codestream SIZ header</p></td>
</tr>
<tr class="odd">
<td align="left"><p>nCConsistentWithSIZ</p></td>
<td align="left"><p>Value of <em>nC</em> from Image Header Box equals <em>csiz</em> from codestream SIZ header</p></td>
</tr>
<tr class="even">
<td align="left"><p>bPCSignConsistentWithSIZ</p></td>
<td align="left"><p>Values of <em>bPCSign</em> from Image Header box (or Bits Per Component box) are equal to corresponding <em>ssizSign</em> values from codestream SIZ header</p></td>
</tr>
<tr class="odd">
<td align="left"><p>bPCDepthConsistentWithSIZ</p></td>
<td align="left"><p>Values of <em>bPCDepth</em> from Image Header box (or Bits Per Component box) are equal to corresponding <em>ssizDepth</em> values from codestream SIZ header</p></td>
</tr>
</tbody>
</table>

 

**  
**

7               Contiguous Codestream box
=========================================

7.1         General codestream structure
----------------------------------------

The Contiguous Codestream box holds the JPEG 2000 codestream, which
contains the actual image data in a JP2.

### Markers and marker segments

A codestream is made up of a number of functional entities which are
called *markers* and *marker segments*. A *marker* is essentially a
2-byte delimiter that delineates the start or end position of a
functional entity. A *marker segment* is the combination of a marker and
a set of associated parameters (*segment parameters*). However, not
every marker has any associated parameters.

### General structure of the codestream

The codestream is made up of the following components (illustrated in
Figure 7‑1):

1.       A *start of codestream* marker that indicates the start of the
codestream

2.       A main codestream header (which includes a number of header
marker segments)

3.       A sequence of one or more *tile parts*. Each tile part consists
of the following components:

a.        A *start of tile-part* marker segment, which indicates the
start of a tile part and which also contains index information of the
tile part and its associated tile

b.       Optionally this may be followed by one or more additional
tile-part header marker segments

c.        A *start of data* marker that indicates the start of�� the
bitstream for the current tile part

d.       The bitstream

4.       An �end of codestream� marker that indicates the end of the
codestream.

![](jpylyzerUserManual_files/image009.gif)

Figure 7‑1 General structure of a JPEG 2000 codestream.

7.2         Limitations of codestream validation
------------------------------------------------

It is important to stress here that *jpylyzer* currently doesn�t support
the full set of marker segments that can occur in a codestream. As a
result, the validation of codestreams is somewhat limited. These
limitations are discussed in this section.

### Main codestream header

Annex A of ISO/IEC 15444-1 lists a total of 13 marker segments that can
occur in the main codestream header. Most of these are optional. The
current version of *jpylyzer* only offers full support (i.e. reads and
validates) for the following main header marker segments (which includes
all the required ones):

�         Start of codestream (SOC) marker segment (required)

�         Image and tile size (SIZ) marker segment (required)

�         Coding style default (COD) marker segment (required)

�         Quantization default (QCD) marker segment (required)

�         Comment (COM) marker segment (optional)

In addition the codestream header may also contain any of the following
marker segments, which are all optional:

�         Coding style component (COC) marker segment
(optional)<sup>\*</sup>

�         Region-of-interest (RGN) marker segment (optional)
<sup>\*</sup>

�         Quantization component (QCC) marker segment (optional)
<sup>\*</sup>

�         Progression order change (POC) marker segment (optional)
<sup>\*</sup>

�         Packet length, main header (PLM) marker segment (optional)
<sup>\*</sup>

�         Packed packet headers, main header (PPM) marker segment
(optional) <sup>\*</sup>

�         Tile-part lengths (TLM) marker segment (optional)
<sup>\*</sup>

�         Component registration (CRG) marker segment (optional)
<sup>\*</sup>

The above marker segments (which are marked with an asterisk) are only
minimally supported at this stage: if *jpylyzer* encounters any of them,
it will include the corresponding element in the *properties* element of
the output. However, *jpylyzer* currently does not analyse the contents
of these marker segments, which means that the respective elements in
the output will be empty.�

### Tile parts

The tile part validation has similar limitations. The standard lists 11
marker segments that can occur in the tile part header. Currently,
*jpylyzer* only fully supports the following ones:

�         Start of tile part (SOT) marker segment (required)

�         Coding style default (COD) marker segment (optional)

�         Quantization default (QCD) marker segment (optional)

�         Comment (COM) marker segment (optional)

�         Start of data (SOD) marker segment (required)

In addition the following optional marker segments may also occur:

�         Coding style component (COC) marker segment
(optional)<sup>\*</sup>

�         Region-of-interest (RGN) marker segment (optional)
<sup>\*</sup>

�         Quantization component (QCC) marker segment (optional)
<sup>\*</sup>

�         Progression order change (POC) marker segment (optional)
<sup>\*</sup>

�         Packet length, tile-part header (PLT) marker segment
(optional) <sup>\*</sup>

�         Packed packet headers, tile-part header (PPT) marker segment
(optional) <sup>\*</sup>

These marker segments (which are marked with an asterisk) are only
minimally supported at this stage: if *jpylyzer* encounters any of them,
it will include the corresponding element in the *properties* element of
the output. However, *jpylyzer* currently does not analyse their
contents, and the respective elements in the output will be empty.�

### Bit streams

In addition to the above limitations, *jpylyzer* can *not* be used to
establish whether the data in the bitstream are correct (this would
require decoding the compressed image data, which is completely out of
*jpylyzer*�s scope)[[16]](#_ftn16).� As a result, if *jpylyzer* is used
as part of a quality assurance workflow, it is recommended to also
include an additional check on the image contents[[17]](#_ftn17). �Also,
*jpylyzer* does not perform any checks on marker segments within the
bit-stream: start-of packet (SOP) and end-of-packet (EPH) markers.

### Detection of incomplete or truncated codestreams

A JP2�s tile part header contains information that makes it possible to
detect incomplete and truncated codestreams in most cases. Depending on
the encoder software used, this method may fail for images that only
contain one single tile part (i.e. images that do not contain tiling).

### Current limitations of comment extraction

Both the codestream header and the tile part header can contain comment
marker segments, which are used for embedding arbitrary binary data or
text. *Jpylyzer* will extract the contents of any comments that are
text.

7.3         Structure of reported output
----------------------------------------

Figure 7‑2illustrates the structure of *jpylyzer*�s codestream-level
output. At the top level, the SIZ, COD, QCD and COM marker segments are
each represented as individual sub elements. The tile part properties
are nested in a *tileParts* element, where each individual tile part is
represented as a separate *tilePart* sub element.

![](jpylyzerUserManual_files/image010.gif)

Figure 7‑2 Structure of codestream-level XML output

 

7.4         Contiguous Codestream box
-------------------------------------

### Element name

contiguousCodestreamBox

### Reported properties

The reported properties for this box are organised into a number groups,
which are represented as child elements in the properties tree:

  

 

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Child element</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>siz (section 7.5)</p></td>
<td align="left"><p>Properties from the image and tile size (SIZ) marker segment (codestream main header)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>cod (section 7.6)</p></td>
<td align="left"><p>Properties from the coding style default (COD) marker segment (codestream main header)</p></td>
</tr>
<tr class="even">
<td align="left"><p>qcd (section 7.7)</p></td>
<td align="left"><p>Properties from the quantization default (QCD) marker segment (codestream main header)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>com (section 7.8)</p></td>
<td align="left"><p>Properties from the (optional) comment (COM) marker segment (codestream main header)</p></td>
</tr>
<tr class="even">
<td align="left"><p>tileParts (section 7.9)</p></td>
<td align="left"><p>Properties from individual tile parts</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>codestreamStartsWithSOCMarker</p></td>
<td align="left"><p>First 2 bytes in codestream constitute a start of codestream (SOC) marker segment</p></td>
</tr>
<tr class="odd">
<td align="left"><p>foundSIZMarker</p></td>
<td align="left"><p>Second marker segment in codestream is image and tile size �(SIZ) marker segment</p></td>
</tr>
<tr class="even">
<td align="left"><p>foundCODMarker</p></td>
<td align="left"><p>Codestream main header contains coding style default (COD) marker segment</p></td>
</tr>
<tr class="odd">
<td align="left"><p>foundQCDMarker</p></td>
<td align="left"><p>Codestream main header contains quantization default (QCD) marker segment</p></td>
</tr>
<tr class="even">
<td align="left"><p>quantizationConsistentWithLevels</p></td>
<td align="left"><p>Values of quantization parameters from QCD marker segment are consistent with <em>levels</em> from COD marker segment<a href="#_ftn18">[18]</a></p></td>
</tr>
<tr class="odd">
<td align="left"><p>foundExpectedNumberOfTiles</p></td>
<td align="left"><p>Number of encountered tiles is consistent with expected number of tiles (as calculated from SIZ marker, see section 7.5)</p></td>
</tr>
<tr class="even">
<td align="left"><p>foundExpectedNumberOfTileParts</p></td>
<td align="left"><p>For all tiles, number of encountered tile parts is consistent with expected number of tile parts (values of <em>tnsot</em> from SOT marker, see section 7.10)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>foundEOCMarker</p></td>
<td align="left"><p>Last 2 bytes in codestream constitute an end of codestream (EOC) marker segment</p></td>
</tr>
</tbody>
</table>

 

 

7.5         Image and tile size (SIZ) marker segment (child of Contiguous Codestream box)
-----------------------------------------------------------------------------------------

### Element name

siz

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>lsiz</p></td>
<td align="left"><p>Length of SIZ marker segment in bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>rsiz</p></td>
<td align="left"><p>Decoder capabilities</p></td>
</tr>
<tr class="even">
<td align="left"><p>xsiz</p></td>
<td align="left"><p>Width of reference grid</p></td>
</tr>
<tr class="odd">
<td align="left"><p>ysiz</p></td>
<td align="left"><p>Heigth of reference grid</p></td>
</tr>
<tr class="even">
<td align="left"><p>xOsiz</p></td>
<td align="left"><p>Horizontal offset from origin of reference grid to left of image area</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yOsiz</p></td>
<td align="left"><p>Vertical offset from origin of reference grid to top of image area</p></td>
</tr>
<tr class="even">
<td align="left"><p>xTsiz</p></td>
<td align="left"><p>Width of one reference tile with respect to the reference grid</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yTsiz</p></td>
<td align="left"><p>Height of one reference tile with respect to the reference grid</p></td>
</tr>
<tr class="even">
<td align="left"><p>xTOsiz</p></td>
<td align="left"><p>Horizontal offset from origin of reference grid to left side of first tile</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yTOsiz</p></td>
<td align="left"><p>Vertical offset from origin of reference grid to top side of first tile</p></td>
</tr>
<tr class="even">
<td align="left"><p>numberOfTiles</p></td>
<td align="left"><p>Number of tiles<a href="#_ftn19">[19]</a></p></td>
</tr>
<tr class="odd">
<td align="left"><p>csiz</p></td>
<td align="left"><p>Number of components</p></td>
</tr>
<tr class="even">
<td align="left"><p>ssizSign<sup>*</sup></p></td>
<td align="left"><p>Indicates whether image component is signed or unsigned (repeated for each component)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>ssizDepth<sup>*</sup></p></td>
<td align="left"><p>Number of bits for this component� (repeated for each component)</p></td>
</tr>
<tr class="even">
<td align="left"><p>xRsiz<sup>*</sup></p></td>
<td align="left"><p>Horizontal separation of sample of this component with respect to reference grid� (repeated for each component)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yRsiz<sup>*</sup></p></td>
<td align="left"><p>Vertical separation of sample of this component with respect to reference grid� (repeated for each component)</p></td>
</tr>
</tbody>
</table>

###  

**  
**

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>lsizIsValid</p></td>
<td align="left"><p><em>lsiz</em> is within range [41,49190]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>rsizIsValid</p></td>
<td align="left"><p><em>rsiz</em> equals 0 (�ISO/IEC 15444-1�), 1 (�Profile 0�) or 2 (�Profile 1�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>xsizIsValid</p></td>
<td align="left"><p><em>xsiz</em> is within range [1,2<sup>32</sup> - 1]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>ysizIsValid</p></td>
<td align="left"><p><em>ysiz</em> is within range [1,2<sup>32</sup> - 1]</p></td>
</tr>
<tr class="even">
<td align="left"><p>xOsizIsValid</p></td>
<td align="left"><p><em>xOsiz</em> is within range [0,2<sup>32</sup> - 2]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yOsizIsValid</p></td>
<td align="left"><p><em>yOsiz</em> is within range [0,2<sup>32</sup> - 2]</p></td>
</tr>
<tr class="even">
<td align="left"><p>xTsizIsValid</p></td>
<td align="left"><p><em>xTsiz</em> <em>�</em>is within range [1,2<sup>32</sup> - 1]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yTsizIsValid</p></td>
<td align="left"><p><em>yTsiz</em> <em>�</em>is within range [1,2<sup>32</sup> - 1]</p></td>
</tr>
<tr class="even">
<td align="left"><p>xTOsizIsValid</p></td>
<td align="left"><p><em>xTOsiz</em> <em>�</em>is within range [0,2<sup>32</sup> - 2]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>yTOsizIsValid</p></td>
<td align="left"><p><em>yTOsiz</em> <em>�</em>is within range [0,2<sup>32</sup> - 2]</p></td>
</tr>
<tr class="even">
<td align="left"><p>csizIsValid</p></td>
<td align="left"><p><em>csiz</em> is within range [1,16384]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>lsizConsistentWithCsiz</p></td>
<td align="left"><p><em>lsiz</em> equals 38 + 3*<em>csiz</em></p></td>
</tr>
<tr class="even">
<td align="left"><p>ssizIsValid<sup>*</sup></p></td>
<td align="left"><p><em>ssizDepth</em> is within range [1,38] (repeated for each component)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>xRsizIsValid<sup>*</sup></p></td>
<td align="left"><p><em>xRsiz</em> is within range [1,255] (repeated for each component)</p></td>
</tr>
<tr class="even">
<td align="left"><p>yRsizIsValid<sup>*</sup></p></td>
<td align="left"><p><em>yRsiz</em> is within range [1,255] (repeated for each component)</p></td>
</tr>
</tbody>
</table>

 

  

 

7.6         Coding style default (COD) marker segment
-----------------------------------------------------

### Element name

cod

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>lcod</p></td>
<td align="left"><p>Length of COD marker segment in bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>precincts</p></td>
<td align="left"><p>Indicates use of precincts (�yes�/�no�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>sop</p></td>
<td align="left"><p>Indicates use of start of packet marker segments (�yes�/�no�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>eph</p></td>
<td align="left"><p>Indicates use of end of packet marker segments (�yes�/�no�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>order</p></td>
<td align="left"><p>Progression order</p></td>
</tr>
<tr class="odd">
<td align="left"><p>layers</p></td>
<td align="left"><p>Number of layers</p></td>
</tr>
<tr class="even">
<td align="left"><p>multipleComponentTransformation</p></td>
<td align="left"><p>Indicates use of multiple component transformation (�yes�/�no�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>levels</p></td>
<td align="left"><p>Number of decomposition levels</p></td>
</tr>
<tr class="even">
<td align="left"><p>codeBlockWidth</p></td>
<td align="left"><p>Code block width</p></td>
</tr>
<tr class="odd">
<td align="left"><p>codeBlockHeight</p></td>
<td align="left"><p>Code block height</p></td>
</tr>
<tr class="even">
<td align="left"><p>codingBypass</p></td>
<td align="left"><p>Indicates use of coding bypass (�yes�/�no�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>resetOnBoundaries</p></td>
<td align="left"><p>Indicates reset of context probabilities on coding pass boundaries� (�yes�/�no�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>termOnEachPass</p></td>
<td align="left"><p>Indicates termination on each coding pass� (�yes�/�no�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>vertCausalContext</p></td>
<td align="left"><p>Indicates vertically causal context� (�yes�/�no�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>predTermination</p></td>
<td align="left"><p>Indicates predictable termination� (�yes�/�no�)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>segmentationSymbols</p></td>
<td align="left"><p>Indicates use of segmentation symbols� (�yes�/�no�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>transformation</p></td>
<td align="left"><p>Wavelet transformation: �9-7 irreversible� or �5-3 reversible�</p></td>
</tr>
<tr class="odd">
<td align="left"><p>precinctSizeX<sup>*</sup></p></td>
<td align="left"><p>Precinct width (repeated for each resolution level; order: low to high) (only if <em>precincts</em> is �yes�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>precinctSizeY<sup>*</sup></p></td>
<td align="left"><p>Precinct heigth (repeated for each resolution level; order: low to high) (only if <em>precincts</em> is �yes�)</p></td>
</tr>
</tbody>
</table>

###  

**  
**

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>lcodIsValid</p></td>
<td align="left"><p><em>lcod</em> is within range [12,45]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>orderIsValid</p></td>
<td align="left"><p><em>order</em> equals 0 (�LRCP�), 1 (�RLCP�), 2 (�RPCL�), 3 (�PCRL�) or 4 (�CPRL�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>layersIsValid</p></td>
<td align="left"><p><em>layers</em> is within range [1,65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>multipleComponentTransformation</p>
<p>IsValid</p></td>
<td align="left"><p><em>multipleComponentTransformation</em> equals 0 or 1</p></td>
</tr>
<tr class="even">
<td align="left"><p>levelsIsValid</p></td>
<td align="left"><p><em>levels</em> is within range [0,32]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>lcodConsistentWithLevelsPrecincts</p></td>
<td align="left"><p><em>lcod</em> equals 12 (<em>precincts</em> = �no�) or <em>lcod</em> equals 13 + <em>levels</em> (<em>precincts</em> = �yes�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>codeBlockWidthExponentIsValid</p></td>
<td align="left"><p><em>codeBlockWidthExponent</em> is within range [2,10]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>codeBlockHeightExponentIsValid</p></td>
<td align="left"><p><em>codeBlockHeightExponent</em> is within range [2,10]</p></td>
</tr>
<tr class="even">
<td align="left"><p>sumHeightWidthExponentIsValid</p></td>
<td align="left"><p><em>codeBlockWidthExponent</em> + <em>codeBlockHeightExponent</em>� ≤� 12</p></td>
</tr>
<tr class="odd">
<td align="left"><p>precinctSizeXIsValid<sup>*</sup></p></td>
<td align="left"><p><em>precinctSizeX</em> ≥ 2 (except lowest resolution level) (repeated for each resolution level; order: low to high) (only if <em>precincts</em> is �yes�)</p></td>
</tr>
<tr class="even">
<td align="left"><p>precinctSizeYIsValid<sup>*</sup></p></td>
<td align="left"><p><em>precinctSizeY</em> ≥ 2 (except lowest resolution level) (repeated for each resolution level; order: low to high) (only if <em>precincts</em> is �yes�)</p></td>
</tr>
</tbody>
</table>

 

  

 

7.7         Quantization default (QCD) marker segment
-----------------------------------------------------

### Element name

qcd

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>lqcd</p></td>
<td align="left"><p>Length of QCD marker segment in bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>qStyle</p></td>
<td align="left"><p>Quantization style for all components</p></td>
</tr>
<tr class="even">
<td align="left"><p>guardBits</p></td>
<td align="left"><p>Number of guard bits</p></td>
</tr>
<tr class="odd">
<td align="left"><p>epsilon<sup>*</sup></p></td>
<td align="left"><p>�         If <em>qStyle</em> equals 0 (�no quantization�): <em>Epsilon</em> exponent in Eq E-5 of ISO/IEC 15444-1 �(repeated for all decomposition levels; order: low to high)</p>
<p>�         If <em>qStyle</em> equals 1 (�scalar derived�): <em>Epsilon</em> exponent in Eq E-3 of ISO/IEC 15444-1</p>
<p>�         If <em>qStyle</em> equals 2 (�scalar expounded�): <em>Epsilon</em> exponent in Eq E-3 of ISO/IEC 15444-1 (repeated for all decomposition levels; order: low to high)</p>
<p> </p></td>
</tr>
<tr class="even">
<td align="left"><p>mu<sup>*</sup></p></td>
<td align="left"><p>�         If <em>qStyle</em> equals 1 (�scalar derived�): <em>mu</em> constant in Eq E-3 of ISO/IEC 15444-1</p>
<p>�         if <em>qStyle</em> equals 2 (�scalar expounded�) : <em>mu</em> constant in Eq E-3 of ISO/IEC 15444-1 (repeated for all decomposition levels; order: low to high)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>lqcdIsValid</p></td>
<td align="left"><p><em>lqcd</em> is within range [4,197]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>qStyleIsValid</p></td>
<td align="left"><p><em>qStyle</em> equals 0 (�no quantization�), 1 (�scalar derived�), or 2 (�scalar expounded�)</p></td>
</tr>
</tbody>
</table>

 

  

 

7.8         Comment (COM) marker segment
----------------------------------------

### Element name

com

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>lcom</p></td>
<td align="left"><p>Length of COM marker segment in bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>rcom</p></td>
<td align="left"><p>Registration value of marker segment (indicates whether this comment contains binary data or text)</p></td>
</tr>
<tr class="even">
<td align="left"><p>comment</p></td>
<td align="left"><p>Embedded comment as text (only if <em>rcom</em> = 1 )</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>lcomIsValid</p></td>
<td align="left"><p><em>lqcd</em> is within range [5,65535]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>rcomIsValid</p></td>
<td align="left"><p><em>rcom</em> equals 0 (�binary�) or 1 (�ISO/IEC 8859-15 (Latin�))</p></td>
</tr>
<tr class="even">
<td align="left"><p>commentIsValid</p></td>
<td align="left"><p>Comment is valid ISO/IEC8859-15 and does not contain control characters, other than tab, newline or carriage return</p></td>
</tr>
</tbody>
</table>

 

  

 

7.9         Tile part (child of Contiguous Codestream box)
----------------------------------------------------------

Tile-part level properties and tests. This is not a box or a marker
segment!

### Element name

tilePart (child of tileParts)

### Reported properties

Each tile part element can contain a number of child elements:

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Child element</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>sot (section 7.10)</p></td>
<td align="left"><p>Properties from start of tile (SOT) marker segment</p></td>
</tr>
<tr class="odd">
<td align="left"><p>cod (section 7.6)</p></td>
<td align="left"><p>Properties from the (optional) coding style default (COD) marker segment (tile part header)</p></td>
</tr>
<tr class="even">
<td align="left"><p>qcd (section 7.7)</p></td>
<td align="left"><p>Properties from the (optional) quantization default (QCD) marker segment (tile part header)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>com (section 7.8)</p></td>
<td align="left"><p>Properties from the (optional) comment (COM) marker segment (tile part header)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>foundNextTilePartOrEOC</p></td>
<td align="left"><p>Tile part start offset + <em>tilePartLength</em> points to either start of new tile or EOC marker (useful for detecting within-codestream byte corruption)</p></td>
</tr>
<tr class="odd">
<td align="left"><p>foundSODMarker</p></td>
<td align="left"><p>Last marker segment of tile part is a start-of-data (SOD) marker</p></td>
</tr>
</tbody>
</table>

 

 

7.10     Start of tile part (SOT) marker segment (child of tile part)
---------------------------------------------------------------------

### Element name

sot

**  
**

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p>lsot</p></td>
<td align="left"><p>Length of SOT marker segment in bytes</p></td>
</tr>
<tr class="odd">
<td align="left"><p>isot</p></td>
<td align="left"><p>Tile index</p></td>
</tr>
<tr class="even">
<td align="left"><p>psot</p></td>
<td align="left"><p>Length of tile part</p></td>
</tr>
<tr class="odd">
<td align="left"><p>tpsot</p></td>
<td align="left"><p>Tile part index</p></td>
</tr>
<tr class="even">
<td align="left"><p>tnsot</p></td>
<td align="left"><p>Number of tile-parts of a tile in the codestream (value of 0 indicates that number of tile-parts of tile in the codestream is not defined in current header)</p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p>lsotIsValid</p></td>
<td align="left"><p><em>lsot</em> equals 10</p></td>
</tr>
<tr class="odd">
<td align="left"><p>isotIsValid</p></td>
<td align="left"><p><em>isot</em> is within range [0,65534]</p></td>
</tr>
<tr class="even">
<td align="left"><p>psotIsValid</p></td>
<td align="left"><p><em>psot</em> is <strong>not</strong> within range [1,13]</p></td>
</tr>
<tr class="odd">
<td align="left"><p>tpsotIsValid</p></td>
<td align="left"><p><em>tpsot</em> is within range [0,254]</p></td>
</tr>
</tbody>
</table>

 

The following marker segments are only minimally supported: *jpylyzer*
will report their presence in the *properties* element, but it does not
perform any further tests or analyses. This may change in upcoming
versions of the software.

7.11     Coding style component (COC) marker segment
----------------------------------------------------

### Element name

coc

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.12     Region-of-interest (RGN) marker segment
------------------------------------------------

### Element name

rgn

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.13     Quantization component (QCC) marker segment
----------------------------------------------------

### Element name

qcc

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.14     Progression order change (POC) marker segment
------------------------------------------------------

### Element name

poc

**  
**

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.15     Packet length, main header (PLM) marker segment
--------------------------------------------------------

### Element name

plm

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.16     Packed packet headers, main header (PPM) marker segment
----------------------------------------------------------------

### Element name

ppm

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

###  

**  
**

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.17     Tile-part lengths (TLM) marker segment
-----------------------------------------------

### Element name

tlm

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.18     Component registration (CRG) marker segment
----------------------------------------------------

### Element name

crg

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.19     Packet length, tile-part header (PLT) marker segment
-------------------------------------------------------------

### Element name

plt

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

7.20     Packed packet headers, tile-part header (PPT) marker segment
---------------------------------------------------------------------

### Element name

ppt

### Reported properties

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Property</p></td>
<td align="left"><p>Description</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

### Tests

<table>
<col width="50%" />
<col width="50%" />
<tbody>
<tr class="odd">
<td align="left"><p>Test name</p></td>
<td align="left"><p>True if</p></td>
</tr>
<tr class="even">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
<tr class="odd">
<td align="left"><p> </p></td>
<td align="left"><p> </p></td>
</tr>
</tbody>
</table>

 

 

**  
**

8               References
==========================

ICC. Specification ICC.1:1998-09 � File Format for Color Profiles.
International Color Consortium, 1998. 29 December 2010
\<[http://www.color.org/ICC-1\_1998-09.pdf](http://www.color.org/ICC-1_1998-09.pdf)\>.

ISO/IEC. Information technology � JPEG 2000 image coding system: Core
coding system. ISO/IEC 15444-1, Second edition. Geneva: ISO/IEC, 2004a.
28 Dec 2010
\<[http://www.jpeg.org/public/15444-1annexi.pdf](http://www.jpeg.org/public/15444-1annexi.pdf)\>
(�Annex I: JP2 file format syntax� only).

ISO/IEC. Information technology � JPEG 2000 image coding system:
Extensions. ISO/IEC 15444-2, First edition. Geneva: ISO/IEC, 2004b. 28
Dec 2010
\<[http://www.jpeg.org/public/15444-2annexm.pdf](http://www.jpeg.org/public/15444-2annexm.pdf)\>
(�Annex M: JPX extended file format syntax� only).

Leach, P., Mealling, M. & Salz, R. A Universally Unique IDentifier
(UUID) URN namespace. Memo, IETF.� July 2005
\<[http://tools.ietf.org/html/rfc4122.html](http://tools.ietf.org/html/rfc4122.html)\>.

  

 

  

* * * * *

[[1]](#_ftnref1) The *jpylyzer* binaries were created using the
*PyInstaller* package:
[http://www.pyinstaller.org/](http://www.pyinstaller.org/)

[[2]](#_ftnref2) Note that *jpylyzer* will not work under Python
versions 3.0-3.1!

 

[[3]](#_ftnref3) Note that *jpylyzer* versions 1.8 and earlier returned
a formatted XML string instead of an element object!

[[4]](#_ftnref4) Note that *jpylyzer* versions 1.4 and earlier used the
verbose output format by default. This behaviour has changed in version
1.5 onwards, as the lengthy output turned out to be slightly confusing
to some users.�

[[5]](#_ftnref5) The �Any ICC� method is defined in ISO/IEC 15444-2 (the
JPX format), and is not allowed in JP2. However, *jpylyzer* offers
limited support for JPX here by also reporting the properties of ICC
profiles that were embedded using this method. Note that any file that
uses this method will fail the �methIsValid� test (and thereby the
validation).

[[6]](#_ftnref6) **Important:** ISO/IEC 15444-1 only allows �input
device� profiles. Support of �display device� profiles will most likely
be added soon through an amendment to the standard. *Jpylyzer* is
already anticipating these changes, but by doing so it is deviating from
the existing standard in the interim period.

[[7]](#_ftnref7) Calculated as: �

[[8]](#_ftnref8) Calculated as:

[[9]](#_ftnref9) Calculated as:

[[10]](#_ftnref10) Calculated as:

[[11]](#_ftnref11) Calculated as: �

[[12]](#_ftnref12) Calculated as:

[[13]](#_ftnref13) Calculated as:

[[14]](#_ftnref14) Calculated as:

[[15]](#_ftnref15) Link:
[http://wwwimages.adobe.com/www.adobe.com/content/dam/Adobe/en/devnet/xmp/pdfs/cs6/XMPSpecificationPart3.pdf](http://wwwimages.adobe.com/www.adobe.com/content/dam/Adobe/en/devnet/xmp/pdfs/cs6/XMPSpecificationPart3.pdf)

[[16]](#_ftnref16) However, support for start of packet (SOP) and end of
packet (EPH) markers may be included in future versions.

[[17]](#_ftnref17) For example, in a TIFF to JP2 conversion workflow one
could include a pixel-by-pixel comparison of the values in the TIFF and
the JP2.

[[18]](#_ftnref18) The consistency check verifies if the length of the
quantization default marker segment (*lqcd* from *qcd*) is consistent
with the quantization style (*qStyle* from *qcd*) and the� number of
decomposition levels (*levels* from *cod*). They are consistent if the
following equation is true:

�

[[19]](#_ftnref19) Calculated as
