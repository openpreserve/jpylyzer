---
layout: post
title: Changes to the User Manual
---
{% include JB/setup %}

Over the last weeks there have been some changes related to the jpylyzer User Manual. Here's a brief overview.

### User Manual now part of website

The *jpylyzer* User Manual is now available online as part of this website. Check out the following link:

[http://openplanets.github.io/jpylyzer/userManual.html](http://openplanets.github.io/jpylyzer/userManual.html)

### Source of User Manual now in Markdown 

This is the first result of an effort to move jpylyzer's documentation away from Microsoft Word:
the source of the User Manual is now entirely written in [Markdown Extra](http://michelf.ca/projects/php-markdown/extra/),
with some [MathML](http://en.wikipedia.org/wiki/MathML) which is used for the equations. 
With the [Pandoc](http://johnmacfarlane.net/pandoc/) tool the Markdown source can be exported to a wide variety of delivery formats.

### Figures as SVG

In addition to this, the figures in the User Manual are now all available as editable [Scalable Vector Graphics](http://en.wikipedia.org/wiki/Scalable_Vector_Graphics) files. These can be found (alongside the 
Markdown source) in the Github repo:

[https://github.com/openplanets/jpylyzer/tree/master/doc](https://github.com/openplanets/jpylyzer/tree/master/doc) 

These changes remove any dependencies on proprietary formats and tools. Hopefully this will make it easier for people to contribute to 
jpylyzer and its documentation.

### Status of PDF

The status of the *PDF* version of the Manual is a bit unclear at this stage: a first test at updating the *PDF* from the Markdown source resulted in 
some issues (the main problem is that some of the tables are not properly fitted to the page), and I'm still looking for a solution for that. 
Perhaps more importantly, I'm not sure if there's real *need* for a PDF version anymore. For now I'll leave the old *PDF* (which is based on the Word document) online.
Needless to say this is only a temporary solution (the Word document will eventually be removed from the repo altogether).
 
