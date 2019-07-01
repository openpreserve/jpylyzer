"""Shared functions for jpylyzer sub-modules"""
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Various shared functions

import sys


def printWarning(msg):
    """Print warning to stderr"""
    msgString = ("User warning: " + msg + "\n")
    sys.stderr.write(msgString)


def errorExit(msg):
    """Print error message to stderr and exit"""
    msgString = ("Error: " + msg + "\n")
    sys.stderr.write(msgString)
    sys.exit()


def consecutive(lst):
    """Returns True if items in lst are consecutive numbers"""
    for i in range(1, len(lst)):
        if lst[i] - lst[i - 1] != 1:
            return False
    return True


def listOccurrencesAreContiguous(lst, value):
    """Returns True if all occurrences of value in lst are at contiguous positions"""
    indices_of_value = [i for i in range(len(lst)) if lst[i] == value]
    return consecutive(indices_of_value)
