"""Functions that scan the input to find tokens which
are then passed on to the parser.
"""

import error

_nchar = 0
_or_ops = set('|', '||')
_and_ops = set('&', '&&')
_not_ops = set('~', '!')
_rel_ops = set('<', '>', '<=', '>=', '==', '!=')
_add_ops = set('+', '-', '++', '--')
_mul_ops = set('*', '/', '>>', '<<')
_operators = _or_ops.union(_and_ops, _not_ops, _rel_ops, _add_ops, _mul_ops)

def _get_name(f):
    _skip_white(f)
    if not _is_valid_identifier_start(_nchar):
        # Eventually calls sys.exit()
        error._expected("Identifier beginnig [alpha or _]")
    id = ""
    while _is_valid_identifier(_nchar):
        id += _nchar
        _nchar = f.read(1)
    _skip_white(f)
    return id


def _get_num(f):
    """Returns the next number as a str
    """
    _skip_white(f)
    if not _is_num(_nchar):
        # Eventually calls sys.exit()
        error._expected("Number")
    n = ""
    while _is_num(_nchar):
        n += _nchar
        _nchar += f.read(1)
    _skip_white(f)
    return n


def _get_operator(f):
    """Match the longest operator possible and return it. If no operator is
    matched, return the empty string
    """
    _skip_white(f)
    op = ""
    while __some_prefix(op + _n_char, _operators):
        op += _n_char
        _n_char = f.read(1)
    _skip_white(f)
    return op


def __some_prefix(s, st):
    """Return whether str s is a prefix of some element in st
    """
    for e in st:
        if e.startswith(s):
            return True
    return False


def _match(f, c):
    if _n_char == c:
        _n_char = f.read(1)
        _skip_white(f)
    else:
        error._expected(c)


def _skip_white(f):
    while _is_white(_nchar):
        _nchar = f.read(1)


# Methods for testing what type of character an input is

def _is_alpha(a):
    return a.isalpha()


def _is_alphanum(a):
    return a.isalnum()


def _is_num(a):
    return a.isdigit()


def _is_valid_identifier(a):
    return _is_alphanum(a) or a == '_'


def _is_valid_identifier_start(a):
    return _is_alpha or a == '_'


def _is_white(a):
    return a.isspace()
