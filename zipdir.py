#!/usr/bin/env python

# Modified from:
# http://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python?answertab=active#tab-top
#
# and:
# http://pymotw.com/2/zipfile/

import os
import zipfile
import argparse

try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED


def zipdir(path, zip):

    nameBase = os.path.basename(path)

    for root, dirs, files in os.walk(path):
        for file in files:

            baseNameRoot = os.path.basename(root)

            if baseNameRoot == nameBase:
                archName = file
            else:
                archName = os.path.basename(root) + "//" + file

            print archName

            zip.write(
                os.path.join(root, file), archName, compress_type=compression)


def parseCommandLine():
    # Create parser
    parser = argparse.ArgumentParser(
        description="zip all files in directory tree")

    # Add arguments
    parser.add_argument('dirIn', action="store", help="input directory")
    parser.add_argument('fileOut', action="store", help="output file")

    # Parse arguments
    args = parser.parse_args()

    return(args)


def main():
    # Get input from command line
    args = parseCommandLine()
    dirIn = args.dirIn
    fileOut = os.path.abspath(args.fileOut)

    zip = zipfile.ZipFile(fileOut, 'w')
    zipdir(dirIn, zip)

    zip.close()

if __name__ == "__main__":
    main()
