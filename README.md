# Jpylyzer homepage

## About
These pages were built with Jekyll Bootstrap 0.3.0:

<http://jekyllbootstrap.com>

The documentation website at <http://jekyllbootstrap.com> is maintained at https://github.com/plusjade/jekyllbootstrap.com

Jekyll Bootstrap is published under the [MIT](http://opensource.org/licenses/MIT) license.

## Maintenance notes

### General site layout
Based on this template:

    /_includes/themes/twitter/default.html

### Use of Liquid variables
To minimise the effort needed to update the site as new *jpylyzer* versions become available, file paths and *jpylyzer* version numbers are defined by *Liquid* variables that can be set/modified in the configuration file:

    _config.yml

For example:
    
    # Version of binary release (update this for each new release!)
    binVersion: 1.10.1
    
    # Prefixes/suffixes that define file paths to binary downloads
    win32Pre: http://dl.bintray.com/openplanets/opf-windows/jpylyzer_
    win32Suf: _win32.zip
    amd64Pre: http://dl.bintray.com/openplanets/opf-debian/jpylyzer_
    amd64Suf: _amd64.deb
    i386Pre: http://dl.bintray.com/openplanets/opf-debian/jpylyzer_
    i386Suf: _i386.deb

In the default site template (see above) the download link to the Win32 executable is then defined as:

    <a href="{{ site.win32Pre }}{{ site.binVersion }}{{ site.win32Suf }}">32 bit</a></p>

Which is rendered by Jekyll as:

    <a href="http://dl.bintray.com/openplanets/opf-windows/jpylyzer_1.10.1_win32.zip">32 bit</a>

So, to update the references to the Windows executables and Debian packages you *only* need to change *binVersion* (assuming that the new binaries follow the existing naming conventions and are stored at the same location).

### Stylesheets
The site uses two stylesheets. First there's the Twitter Bootstrap stylesheet, which should be left as it is (don't edit this!):

    /assets/themes/twitter/bootstrap/css/bootstrap.2.2.2.min.css

In addition there's a stylesheet with user-defined styles that can be used to define your own styles, or override the Twitter Bootstrap ones:

    /assets/themes/twitter/css/style.css

### Adding news items
News items are stored as *Markdown* files in the *\_posts* folder. File naming convention:

    yyyy-mm-dd-Title-of-Post.md

Most recent posts (3) will automatically show up in *Latest news* bar on top of homepage.

### Updating the User Manual section

Steps:

1. Export the master (Markdown) jpylyzer manual file to HTML with Pandoc:

    pandoc -s --toc --toc-depth=2 --ascii -N -c jpylyzer.css -w html5 
    -T "jpylyzer User Manual"  -o jpylyzerUserManual.html jpylyzerUserManual.md 

(See also [instructions here](https://github.com/openpreserve/jpylyzer/tree/master/doc#export-to-html))

1. Open the file in a text editor and copy everything between the *<body>* and *</body>* tags (without including these tags themselves!)

1. Open the file [userManual.html](userManual.html) in a text editor, delete everything below the title text (i.e. *{h1}User Manual{/h1}*), and paste in text from the previous step.

1. Save file. Done!

Obviously this is a bit clumsy, and should be automated at some point. In any case do **not** copy the Pandoc-generated HTML file directly, as styles/formatting will break.
 
 


