#jpylyzer

## About
*Jpylyzer* is a JP2 [(JPEG 2000 Part 1)][2] image validator and properties extractor. Its development was partially supported by the [SCAPE][4] Project. The SCAPE project is co-funded by the European Union under FP7 ICT-2009.4.1 (Grant Agreement number 270137).

## Jpylyzer homepage

<http://jpylyzer.openpreservation.org/>

## Downloads

* [User Manual][1] - exhaustive documentation of all aspects of *jpylyzer*
* [Windows binaries][5] - stand-alone Windows binaries that allow you to run *jpylyzer* without any *Python* dependencies
* [Debian packages][6] - i386 (32 bit) architecture
* [Debian packages][7] - Amd 64 (64 bit) architecture


## Command line use

### Usage

    usage: jpylyzer.py [-h] [--verbose] [--recurse] [--wrapper] [--nullxml]
                       [--nopretty] [--version] jp2In [jp2In ...]

### Positional arguments

`jp2In` : input JP2 image(s), may be one or more (whitespace-separated) path expressions; prefix wildcard (\*) with backslash (\\) in Linux..

### Optional arguments

`-h, --help` : show this help message and exit;

`-v, --version` : show program's version number and exit;

`--verbose` : report test results in verbose format;

`--recurse, -r` : when analysing a directory, recurse into subdirectories (implies `--wrapper`)

`--wrapper, -w` : wrap the output for individual image(s) in 'results' XML element.

`--nullxml` : extract null-terminated XML content from XML and UUID boxes (doesn't affect validation)

`--nopretty` : suppress pretty-printing of XML output

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

## Debian packages build process

The [Vagrant directory](vagrant) of this repo contains instructions on how to build Debian packages using [VirtualBox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/). A Vagrantfile and provisioning scripts are included for a number of target platforms, which should make the process of building the packages fairly easy.

## Steps in preparing a jpylyzer release

(Outline only, this section is under development and needs more detail!).

1. Make changes to code
1. Update version number in *jpylyzer.py*, *setup.py* and *sonar-project.properties* (do we really need last file?)
1. In case of changes to command-line interface, update [jpylyzer.pod](debian/jpylyzer.pod) file in *Debian* folder.
1. Create new entry in changelog using `dch -i`; then manually update version number, and create list of changes.
1. Update [User Manual](doc/jpylyzerUserManual.md) if necessary
1. Commit all changes
1. Add tag and commit
1. Build Linux packages using [instructions here](vagrant)
1. Build Windows binaries
1. Upload Linux/Windows packages to BinTray
1. Website: update *binVersion* in *_config.yml* (this updates the links to all packages on BinTray to the correct version)
1. Website: write short release note
1. Commit changes to website
1. Spread the word!

  
[1]: https://github.com/openplanets/jpylyzer/blob/master/doc/jpylyzerUserManual.pdf?raw=true
[2]: http://www.jpeg.org/public/15444-1annexi.pdf
[3]: http://www.itu.int/rec/T-REC-T.800/en
[4]: http://www.scape-project.eu/
[5]: https://bintray.com/openplanets/opf-windows/jpylyzer_win32/
[6]: https://bintray.com/openplanets/opf-debian/jpylyzer_i386/
[7]: https://bintray.com/openplanets/opf-debian/jpylyzer_amd64/
