"""Functions that signal an error has been encountered
"""

import sys

def _error(msg):
    print(msg)
    sys.exit()


def _expected(value):
    _error("Expected: " + str(value))
