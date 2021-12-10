# Jpylyzer output schema

## About the schema
This folder contains a first attempt at an output schema for jpylyzer. A couple of notes on the schema:

* The current schema doesn't include the *tests* element, which is skipped. (Would anyone really need this in the first place?)
* No elaborate checks on reported properties (apart from data type); this is all done by *jpylyzer* anyway.
* All boxes + properties that can be reported in the *properties* element are included in the schema.
* The schema doesn't impose any constraints on whether the box types that are reported directly under *properties* (or in any of the superboxes) are actually allowed there. *Jpylyzer* just parses a *JP2* and reports whatever it finds there. Checks on whether boxes are allowed at a particular location, all expected boxes are present and their order of appearance are all part of *jpylyzer*'s validation process, and aren't repeated in the schema. If *jpylyzer* decides that a file is not valid *JP2* because of such constraints, the resulting output XML should still be valid according to *jpylyzer*'s output schema.
* Some numerical output elements that now have the *decimal* type could possibly result in validation errors in extreme cases (e.g. output in scientific notation for very large values). If this turns out to be a real problem, consider changing the vtype to *double* for those fields (already did this for *compressionRatio*, which can get huge in case of truncated files).

## Files

* **jpylyzer-v-1-0.xsd** - schema
* **test_allboxes.xml** - synthetic output file that contains all possible box types that jpylyzer is able to report
* **test_wrapper.xml** - synthetic output file with multiple *jpylyzer* elements that are wrapped in a *results* element (`--wrapper` option)

## Published schema location

Here: <http://jpylyzer.openpreservation.org/jpylyzer-v-1-0.xsd>. 

For updates, use the branch of this repo that holds the jpylyzer homepage:

<https://github.com/openpreserve/jpylyzer/tree/gh-pages>

In case of changes that are bug fixes, publish the fixed schema under *exactly* the same name as the old one. In case of major changes, add the new schema as a separate file (e.g. *jpylyzer-v-2.0.xsd*) and then update declaration in jpylyzer as well. This will keep old instance files from breaking.

## Validate jpylyzer output file against schema

Using [xmllint](http://xmlsoft.org/xmllint.html):

### Local schema instance

    xmllint --noout --schema jpylyzer-v-1-0.xsd test_allboxes.xml 

Result:

    test_allboxes.xml validates

### Published schema

    xmllint --noout --schema http://jpylyzer.openpreservation.org/jpylyzer-v-1-0.xsd test_allboxes.xml 

Result:

    test_allboxes.xml validates
