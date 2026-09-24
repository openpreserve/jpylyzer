#! /usr/bin/env python3

import sys

# Shared functions for jpylyzer sub-modules


def printWarning(msg):
    """Print warning to stderr."""
    msgString = "User warning: " + msg + "\n"
    sys.stderr.write(msgString)


def errorExit(msg):
    """Print error message to stderr and exit."""
    msgString = "Error: " + msg + "\n"
    sys.stderr.write(msgString)
    sys.exit()

