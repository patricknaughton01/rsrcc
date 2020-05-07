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
    if identifier in _keywords:
        error._error("Variable shadows keyword: " + str(identifier))
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
    while scanner._n_char != '}':
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
    op = scanner._get_operator(f)
    if op in scanner._not_ops:
        _factor(f)
        if op == '~':
            # Bitwise not the tos
            pass
        elif op == '!':
            # Logical not the tos
            pass
    elif op == '':
        _relation(f)
    else:
        error._expected('factor or not-op')


def _relation(f):
    _a_expression(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._rel_ops:
            error._expected('rel op')
        _a_expression(f)
        op = scanner._get_operator(f)


def _a_expression(f):
    _a_term(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._add_ops:
            error._expected('add op')
        _a_term(f)
        op = scanner._get_operator(f)


def _a_term(f):
    _a_factor(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._mul_ops:
            error._expected('mul op')
        _a_factor(f)
        op = scanner._get_operator(f)


def _a_factor(f):
    op = scanner._get_operator(f)
    if op in scanner._add_ops:
        _a_factor(f)
        if op == '-':
            # Negate the tos, if + we don't have to do anything
            pass
    elif op == '':
        if scanner._n_char == '(':
            scanner._match('(')
            _expression(f)
            scanner._match(')')
        elif scanner._is_valid_identifier_start(scanner._n_char):
            id = scanner._get_name(f)
            # Do something with the identifier (push value to tos?)
            # TODO: determine if var or function
        elif scanner._is_num(scanner._n_char):
            n = scanner._get_num(f)
            # Do something with the number (push to tos?)
    else:
        error._expected('a_factor or add-op')
