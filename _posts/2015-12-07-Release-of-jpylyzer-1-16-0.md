---
layout: post
title: Release of jpylyzer 1.16.0 
---
{% include JB/setup %}

Hot on the heels of last week's 1.15 release, here's *jpylyzer* 1.16.0! Note that this release includes a small change in *jpylyzer*'s output format, which may have an impact on existing workflows. 

### Improved exception handling

In previous releases of *jpylyzer*, an exception during the processing of an image could lead to a crash. For example, an extremely large image could result in an internal memory error, and this would grind *jpylyzer* to a halt. This is particularly problematic for (recursive) scans of whole directory trees: in this case a single *jpylyzer* invocation may involve the processing of thousands of images at a time. One single (e.g. extremely large) image could then result in unusable output; moreover, it would be difficult to identify *which* image caused the crash in the first place! Release 1.16.0 includes improved exception handling that allows *jpylyzer* to handle such situations more gracefully. If an image causes an exception, *jpylyzer* will report the failure in the output, after which it will continue processing the remaining images.

### New statusInfo output element

In order to make this all work, the output for each analysed file now includes a *statusInfo* element. It tells you whether 
the validation process could be completed without any internal errors. It contains the following sub-elements:

* *success*: a Boolean flag that indicates whether the validation attempt 
completed normally (“True”) or not (“False”). A value of “False” indicates
an internal error that prevented *jpylyzer* from validating the file. 

* *failureMessage*: if the validation attempt failed (value of *success* 
equals “False”), this field gives further details about the reason of the failure.

As an example, here's the output for 6.5 GB JP2 that caused a memory error:

    <?xml version='1.0' encoding='UTF-8'?>
    <jpylyzer>
        <toolInfo>
            <toolName>jpylyzer.py</toolName>
            <toolVersion>1.16.0</toolVersion>
        </toolInfo>
        <fileInfo>
            <fileName>AS16-P-4102.jp2</fileName>
            <filePath>/home/johan/testJpylyzer/AS16-P-4102.jp2</filePath>
            <fileSizeInBytes>6745365021</fileSizeInBytes>
            <fileLastModified>Wed Dec  2 20:05:29 2015</fileLastModified>
        </fileInfo>
        <statusInfo>
            <success>False</success>
            <failureMessage>memory error (file size too large)</failureMessage>
        </statusInfo>
        <isValidJP2>False</isValidJP2>
        <tests/>
        <properties/>
    </jpylyzer>

This means that the general structure of the output now looks like this:

![]({{ BASE_PATH }}/images/outputStructure.png) 

### New XSD schema

The change to the output format also made it necessary to update the XSD schema. The new version [can be found here](http://jpylyzer.openpreservation.org/jpylyzer-v-1-1.xsd). The old schema will remain available.






