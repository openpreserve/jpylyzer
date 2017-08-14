# How to build the Windows binaries


## Prerequisites

Windows binaries are now built under Linux using [Wine](https://www.winehq.org/). Make sure you have a recent version of Wine installed. Also check if (a recent version of) the *winbind* package is installed. If not, install it using:

    sudo apt-get install winbind

## Building the binaries

In your console window, go to the root of the jpylyzer directory. Then run:

    ./buildwin.sh
    
The script first checks for the presence of (portable) 64 and 32 versions of Python 2.7 under *Wine*, and installs them if they are not found. Note that the installers need some manual input. Most importantly, make sure you enter the following installation paths:

* `C:\Python27_64` for the 64-bit version;

* `C:\Python27_32` for the 32-bit version.

The script also automatically installs PyInstaller ifit is not there already.

Once the above dependencies are installed, 64 and 32 bit binaries are built automatically. The (zipped) binaries can be found in the *dist* directory.

## Troubleshooting

If the output of the build script includes this error:

    err:winediag:SECUR32_initNTLMSP ntlm_auth was not found or is outdated. Make sure that ntlm_auth >= 3.0.25 is in your path. Usually, you can find it in the winbind package of your distribution.

Fix this by installing *winbind* (see the top of this page).


 