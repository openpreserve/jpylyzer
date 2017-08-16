# How to build stand-alone Linux binaries

To build stand-alone Linux binaries, simply run the *build-with-pyinstaller.sh* script from the jpylyzer root directory:

    ./build-with-pyinstaller.sh

This will create the binaries under *pyi-build/dist*. The build script requires PyInstaller. If PyInstaller is not installled, it can be installed using:

    (sudo) pip install pyinstaller

(If you don't know if you have PyInstaller just run the build script, which will display a message id it cannot find PyInstaller.)
