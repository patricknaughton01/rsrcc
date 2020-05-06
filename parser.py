"""Parser for the program to convert tokens into object code.
"""

import error
import codegen
import scanner

from enum import Enum

_keywords = set('if', 'while', 'function', 'var')
_symtab = {}


def _program(f):
    while scanner._nchar != '}':
        name = scanner._get_name(f)
        if name == 'var':
            _global_var(f)
        elif name == 'function':
            _function(f)
        else:
            error._expected("Variable or function declaration")


def _global_var(f):
    identifier = scanner._get_name(f)
    if identifier in _symtab:
        # Eventually calls sys.exit()
        error._error("Duplicate symbol variable: " + str(identifier))
    if scanner._n_char == '=':
        # This variable is initialized
        scanner._match('=')
        pass
    else:
        # No initialization
        pass


def _function(f):
    identifier = scanner._get_name(f)
    if identifier in _symtab:
        # Eventually calls sys.exit()
        error._error("Duplicate symbol function: " + str(identifier))
    scanner._match('(')
    # Do something with parameter list
    scanner._match(')')
    scanner._match('{')
    _block(f)
    scanner._match('}')


def _block(f):
    pass


def _expression(f):
    _term(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._or_ops:
            error._expected('or operator')
        _term(f)
        op = scanner._get_operator(f)


def _term(f):
    _factor(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._and_ops:
            error._expected('and operator')
        _factor(f)
        op = scanner._get_operator(f)


def _factor(f):
    pass


def _relation(f):
    pass


def _a_expression(f):
    pass


def _a_term(f):
    pass


def _a_actor(f):
    pass
