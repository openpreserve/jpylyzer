#! /usr/bin/env python3
"""
Shared functions for jpylyzer sub-modules
"""

import sys


def printWarning(msg):
    """Print warning to stderr."""
    msgString = "User warning: " + msg + "\n"
    sys.stderr.write(msgString)


def errorExit(msg):
    """Print error message to stderr and exit."""
    msgString = "Error: " + msg + "\n"
    sys.stderr.write(msgString)
    sys.exit()
