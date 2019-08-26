
import sys

def printWarning(msg):
    """Print warning to stderr"""
    msgString = ("User warning: " + msg + "\n")
    sys.stderr.write(msgString)

def main():
    failureMessage = "runtime error, please report to developers by creating " + \
                     "an issue at https://github.com/openpreserve/jpylyzer/issues"

    printWarning(failureMessage)

main()
