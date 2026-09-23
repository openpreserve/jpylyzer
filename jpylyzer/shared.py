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


def consecutive(lst):
    """Return True if items in lst are consecutive numbers."""
    for i in range(1, len(lst)):
        if lst[i] - lst[i - 1] != 1:
            return False
    return True


def listOccurrencesAreContiguous(lst, value):
    """Return True if all occurrences of value in lst are at contiguous positions."""
    indices_of_value = [i for i in range(len(lst)) if lst[i] == value]
    return consecutive(indices_of_value)
