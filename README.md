#jpylyzer

## About
*Jpylyzer* is a JP2 [(JPEG 2000 Part 1)][2] image validator and properties extractor. Its development was partially supported by the [SCAPE][4] Project. The SCAPE project is co-funded by the European Union under FP7 ICT-2009.4.1 (Grant Agreement number 270137).

## Downloads

* [User Manual][1] - exhaustive documentation of all aspects of *jpylyzer*
* [Windows binaries][5] - stand-alone Windows binaries that allow you to run *jpylyzer* without any *Python* dependencies 


## Command line use

### Usage
`usage: jpylyzer.py [-h] [--verbose] [--wrapper] [--version] ...`

### Positional arguments

`...` : input JP2 image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux..

### Optional arguments

`-h, --help` : show this help message and exit;

`-v, --version` : show program's version number and exit;

`--verbose` : report test results in verbose format;

`--wrapper, -w` : wrap the output for individual image(s) in 'results' XML element.

## Output 
Output is directed to the standard output device (*stdout*).

### Example

`jpylyzer.py rubbish.jp2 > rubbish.xml`

In the above example, output is redirected to the file 'rubbish.xml'.


### Outline of output elements

1. *toolInfo*: tool name (jpylyzer) + version.
2. *fileInfo*: name, path, size and last modified time/date of input file.
3. *isValidJP2*: *True* / *False* flag indicating whether file is valid JP2.
4. *tests*: tree of test outcomes, expressed as *True* / *False* flags.
   A file is considered valid JP2 only if all tests return *True*. Tree follows JP2 box structure. By default only tests that returned *False* are reported, which results in an empty *tests*  element for files that are valid JP2. Use the  `--verbose` flag to get *all* test results.
5. *properties*: tree of image properties. Follows JP2 box structure. Naming of properties follows [ISO/IEC 15444-1 Annex I][2] (JP2 file format syntax) and [Annex A][3] (Codestream syntax).
   
[1]: https://github.com/openplanets/jpylyzer/blob/master/doc/jpylyzerUserManual.pdf
[2]: http://www.jpeg.org/public/15444-1annexi.pdf
[3]: http://www.itu.int/rec/T-REC-T.800/en
[4]: http://www.scape-project.eu/
[5]: https://bintray.com/pkg/show/general/openplanets/binaries/jpylyzer

## Changes

###1.10
Added *setup.py* and re-structured repo accordingly. This means that *jpylyzer* can now be built and installed with *distutils*.

###1.9
The following improvements were added by Adam Retter and Jaishree Davey of The National Archives (UK):

1. Unicode output
2. Possibility to specify multiple (sets of) images at command-line
3. Wrapper option that results in well-formed XML in case of multiple input images
4. Function *checkOneFile* now returns Element object (before: text string with XML) 

In addition, this version includes several minor modifications that improve interoperability between Python 2.7 and Python 3. 

###1.8
Added support for XMP metadata that are embedded in a UUID box.

###1.7
Added minimal support of the following optional codestream marker segments that were missing in previous versions:

   + Coding style component (COC) marker segment
   + Region-of-interest (RGN) marker segment
   + Quantization component (QCC) marker segment
   + Progression order change (POC) marker segment
   + Packet length, main header (PLM) marker segment
   + Packed packet headers, main header (PPM) marker segment
   + Tile-part lengths (TLM) marker segment
   + Component registration (CRG) marker segment
   + Packet length, tile-part header (PLT) marker segment
   + Packed packet headers, tile-part header (PPT) marker segment

For now jpylyzer just reports the presence of these marker segments if they were found in an image, without doing validating them or reporting any properties (i.e. the validator functions are empty).
