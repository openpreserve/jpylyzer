---
layout: page
title: Installation
---
{% include JB/setup %}

## Installation

For installing *jpylyzer*, you have three options:

1. Install with the *Pip* package manager. This works on all platforms
(Windows, Linux, Mac, etc.), but you need to have the Python interpreter
available on your system. *Jpylyzer* is compatible with Python 3.2 and more recent (starting with Jpylylyzer 2.2, Python 2.7 is no longer supported).

2. Alternatively, for Windows users stand-alone binaries are available.
These allow you to run *jpylyzer* as anexecutable Windows application,
without any need for installing Python. This option is particularly useful
for Windows users who cannot (or don’t want to) install software on their system.

3. For Linux users Debian packages are available.

These options are briefly outlined below. See the [User Manual]({{ BASE_PATH }}/userManual.html)
for a more exhaustive description.

## Installation with Pip (all platforms)

First make sure you have a recent version of *pip*. Then install *jpylyzer*
with the following command:

    pip install jpylyzer

This may require administrator/super user privileges. If you don't have these
privilges, you can do a single-user install:

    pip install jpylyzer --user

## Windows binaries

Download the binary (64 or 32 bit) using the link using the link in the right-hand bar of
this page. Unzip the contents of this file to an empty folder on your PC. *Jpylyzer* should
now be ready for use.

Optionally, you may also want to add the full path of the *jpylyzer*
installation directory to the Windows ’Path’ environment variable. Doing
so allows you to run *jpylyzer* from any directory on your PC without
having to type the full path. In Windows 7 you can do this by selecting
‘settings’ from the ‘Start’ menu; then go to ‘control panel’/’system’
and go to the ‘advanced’ tab. Click on the ‘environment variables’
button. Finally, locate the ‘Path’ variable in the ‘system variables’
window, click on ‘Edit’ and add the full *jpylyzer* path (this requires
local Administrator privileges). The settings take effect on any newly
opened command prompt.

## Installation from Debian packages (Linux)

For Linux, Debian packages of *jpylyzer* exist.
To install, simply download the *.deb* file, double-click on it and
select *Install Package*. Alternatively you can also do this in the
command terminal by typing:

    sudo dpkg -i opf-jpylyzer_2.0.0_all.deb

In both cases you need to have administrative privileges.

For *Ubuntu* and *Debian* alternative packages are available in the
official release channels. To install simply run the following commands:

    sudo apt-get update
    sudo apt-get install python-jpylyzer

In both cases you need to have superuser privileges.

A more exhaustive description of the above installation options can be found in the [User Manual]({{ BASE_PATH }}/doc/latest/userManual.html).
