# Various shared functions

import sys

def printWarning(msg):
    msgString=("User warning: %s\n") % (msg)
    sys.stderr.write(msgString)

def consecutive(lst):
    # Returns True if items in lst are consecutive numbers
    for i in range(1,len(lst)):
        if lst[i] - lst[i-1] != 1:
            return False
    return True

def listOccurrencesAreContiguous(lst, value):
    # True if all occurrences of value in lst are at contiguous positions
    indices_of_value = [i for i in range(len(lst)) if lst[i] == value]
    return consecutive(indices_of_value)
