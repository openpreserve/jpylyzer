Jpylyzer is a JP2 (JPEG 2000 Part 1) image validator and properties 
extractor. Jpylyzer was specifically created to check that a JP2 file really
conforms to the format's specifications. Additionally jpylyzer is able to
extract a JP2's technical characteristics.

Requires Python 2.7 or later

usage: jpylyzer.py [-h] [--verbose] [--wrapper] [--version] ... 

~Positional arguments~ 

... : input JP2 image(s), may be one or more (whitespace-separated) path 
expressions; prefix wildcard (*) with backslash (\) in Linux.. 

~Optional arguments~ 

-h, --help : show this help message and exit; 

-v, --version : show program's version number and exit; 

--verbose : report test results in verbose format; 

--wrapper, -w : wrap the output for individual image(s) in 'results' XML 
element. Output 

Output is directed to the standard output device (stdout).

Development partially supported by the SCAPE Project. 
The SCAPE project is co-funded by the European Union under FP7 
ICT-2009.4.1 (Grant Agreement number 270137).
