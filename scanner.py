"""Functions that scan the input to find tokens which
are then passed on to the parser.
"""

import error

_nchar = 0
_or_ops = {'|', '||'}
_and_ops = {'&', '&&'}
_not_ops = {'~', '!'}
_rel_ops = {'<', '>', '<=', '>=', '==', '!='}
_add_ops = {'+', '-', '++', '--'}
_mul_ops = {'*', '/', '>>', '<<'}
_operators = _or_ops.union(_and_ops, _not_ops, _rel_ops, _add_ops, _mul_ops)


def _get_name(f):
    global _nchar
    _skip_white(f)
    if _nchar == '':
        return ''
    if not _is_valid_identifier_start(_nchar):
        # Eventually calls sys.exit()
        error._expected("Identifier beginning [alpha or _]")
    id = ""
    while _is_valid_identifier(_nchar):
        id += _nchar
        _nchar = f.read(1).decode("utf-8")
    return id


def _get_num(f):
    """Returns the next number as a str
    """
    global _nchar
    _skip_white(f)
    if _nchar == '':
        return ''
    if not _is_num(_nchar):
        # Eventually calls sys.exit()
        error._expected("Number")
    n = ""
    while _is_num(_nchar):
        n += _nchar
        _nchar = f.read(1).decode("utf-8")
    return n


def _get_operator(f):
    """Match the longest operator possible and return it. If no operator is
    matched, return the empty string
    """
    global _nchar, _operators
    _skip_white(f)
    op = ""
    if _nchar == '':
        return ''
    while __some_prefix(op + _nchar, _operators):
        op += _nchar
        _nchar = f.read(1).decode("utf-8")
    return op


def __some_prefix(s, st):
    """Return whether str s is a prefix of some element in st
    """
    if s == '':
        return False
    for e in st:
        if e.startswith(s):
            return True
    return False


def _match(f, c):
    global _nchar
    _skip_white(f)
    if _nchar == c:
        _nchar = f.read(1).decode("utf-8")
    else:
        error._expected(c)


def _skip_white(f):
    global _nchar
    while _is_white(_nchar):
        _nchar = f.read(1).decode("utf-8")


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
    return _is_alpha(a) or a == '_'


def _is_white(a):
    return a.isspace()
