def consecutive(lst):
    """Returns True iff items in lst are consecutive numbers"""
    for i in xrange(1, len(lst) - 1):
        if lst[i] - lst[i-1] != 1:
            return False
    return True

def listOccurrencesAreContiguous(lst, value):
    """True iff all occurrences of value in lst are at contiguous positions"""
    indices_of_value = [i for i in xrange(len(lst)) if lst[i] == value]
    return consecutive(indices_of_value)
