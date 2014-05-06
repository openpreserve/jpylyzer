#Notes on jpylyzer User Manual

## Syntax

The jpylyzer User Manual uses the [Markdown Extra](http://michelf.ca/projects/php-markdown/extra/) syntax. This Markdown version differs in a number of ways from [GitHub Flavored Markdown](https://help.github.com/articles/github-flavored-markdown), and as a result the Markdown file doesn't render correctly when viewed in Github. This is no reason for any concern.

For the rendering of the equation objects (which are in [MathML](http://en.wikipedia.org/wiki/MathML)) there is a dependency on [MathJax](http://www.mathjax.org/)

## Exporting to other delivery formats

Use [Pandoc](http://johnmacfarlane.net/pandoc/) to export the raw Markdown file. For example, to generate the User Manual in HTML format use the following command-line:

    pandoc -s --toc --toc-depth=2 --ascii -N -c jpylyzer.css -f markdown_phpextra -w html5 jpylyzerUserManual.md -o jpylyzerUserManual.html

Note on command-line switches:

* `-s` creates a stand-alone file
* `--toc` automatically generates a table of contents
* `--toc-depth=2` specifies that table of contents contains Chapter (level 1) and Section (level 2) headings (so level 3 and higher are left out).
* `--ascii` generates output in ascii format (not sure if this is really needed?)
* `-N` activates automatic chapter/section/subsection numbering
* `-f` sets the input format to `markdown_phpextra`
* `-w html5` sets the output format to `html 5` (important, because document contains MathML content that is not supported in previous html versions) 
* `-c jpylyzer.css` defines style sheet
<!-- * `--self-contained` embeds css and images inside the file -->

You will need a fairly recent version of *Pandoc* to make this work, as older versions do not support `markdown_phpextra` as an input format.

## Stylesheet
The stylesheet *jpylyzer.css* is based on John MacFarlane's [pandoc.css](http://johnmacfarlane.net/pandoc/demo/pandoc.css), with some adaptations.

