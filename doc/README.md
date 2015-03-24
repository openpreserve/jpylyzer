# Notes on jpylyzer User Manual

## Syntax

The jpylyzer User Manual uses the [Markdown Extra](http://michelf.ca/projects/php-markdown/extra/) syntax with some Pandoc-specific extras. This Markdown version differs in a number of ways from [GitHub Flavored Markdown](https://help.github.com/articles/github-flavored-markdown), and as a result the Markdown file doesn't render correctly when viewed in Github. This is no reason for any concern.

For the rendering of the equation objects (which are in [MathML](http://en.wikipedia.org/wiki/MathML)) there is a dependency on [MathJax](http://www.mathjax.org/)

## Exporting to HTML

Run the script [mdToDeliveryFormats.sh](mdToDeliveryFormats.sh) to export the Markdown file to the folllowing delivery formats:

1. Jekyll template with HTML that can be used to replace the on-line manual on the jpylyzer homepage (file  [userManual.html](https://github.com/openpreserve/jpylyzer/blob/gh-pages/userManual.html))

1. Self-contained HTML without any external dependencies (style sheets, images etc. are all embedded in one single file; this replaces the former PDF version).

Script requires [Pandoc](http://johnmacfarlane.net/pandoc/) and [Xmllint](http://xmlsoft.org/xmllint.html).

Note on the command-line switches used in the script:

* `-s` creates a stand-alone file
* `--toc` automatically generates a table of contents
* `--toc-depth=2` specifies that table of contents contains Chapter (level 1) and Section (level 2) headings (so level 3 and higher are left out).
* `--ascii` generates output in ascii format (not sure if this is really needed?)
* `-N` activates automatic chapter/section/subsection numbering
* `-w html5` sets the output format to `html 5`
* `-c jpylyzer.css` defines style sheet

You will need a fairly recent version of *Pandoc* to make this work, as older versions do not support `markdown_phpextra` as an input format. Note that it is important to use html5 as the output format, because the Markdown file contains [MathML](http://nl.wikipedia.org/wiki/Mathematical_Markup_Language) content that is not supported in previous html versions. 

## Export to other delivery formats

Could be included at later stage. So far I have briefly investigated te following.

### PDF
First attempt, after some experimentation:

    pandoc -s --toc --toc-depth=2 -N --chapters --latex-engine=xelatex -o jpylyzerUserManual.pdf jpylyzerUserManual.md

This results in a PDF, but it has a number of issues:

* Equations are mangled
* Some of the tables don't fit on the page (cell contents aren't wrapped)
* Size of images isn't quite right.

### EPUB3

    pandoc -S -N --chapters -w epub3 --epub-stylesheet jpylyzer.css -o jpylyzerUserManual.epub frontMatter.md jpylyzerUserManual.md

This produces a file that is valid EPUB 3 according to [epubcheck](https://github.com/idpf/epubcheck).

Issues:

* Equations are mangled
* TOC numbering isn't quite right.

Because of the many issues with the PDF and EPUB export I'll be sticking to HTML for now.

## Stylesheet
The stylesheet *jpylyzer.css* is based on John MacFarlane's [pandoc.css](http://johnmacfarlane.net/pandoc/demo/pandoc.css), with some adaptations.

## Figures
The directory `figuresSVG` contains the Figures in [SVG](http://en.wikipedia.org/wiki/Scalable_Vector_Graphics) format. If you ever need to change/modify any of the figures in the manual, try editing the SVG (e.g. in [Inkscape](http://www.inkscape.org/)), then export the updated image to PNG. Note that the SVGs were derived from an MS Powerpoint file, and I'm not 100% sure as to how easy it is to edit them. 

For best results in Inkscape:

* select all the Figure elements by drawing a rectangle around them; 
* then use *Export Bitmap* from the *File* menu; 
* set the *Export area* to *Selection*, and *Width* to a value between 350 (smaller figures) and 400 (larger ones);
* export result to directory *images*, using the same base name as the SVG.  
