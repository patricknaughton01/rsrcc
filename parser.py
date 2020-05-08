"""Parser for the program to convert tokens into object code.
"""

import error
import codegen
import scanner

GLOBAL_PREFIX = "GL"

_keywords = {'if', 'while', 'function', 'var'}
_symtab = {}
_label_count = 0


def _program(f):
    name = scanner._get_name(f)
    while name == 'var':
        _global_var(f)
        name = scanner._get_name(f)
    while name == 'function':
        _function(f)
        name = scanner._get_name(f)


def _global_var(f):
    global _symtab, _keywords
    identifier = scanner._get_name(f)
    if identifier in _symtab:
        # Eventually calls sys.exit()
        error._error("Duplicate symbol variable: " + str(identifier))
    if identifier in _keywords:
        error._error("Variable shadows keyword: " + str(identifier))
    label = GLOBAL_PREFIX + str(_next_label())
    codegen._alloc_global(label)
    _symtab[identifier] = {'type': 'global_var'}
    if scanner._nchar == '=':
        # This variable is initialized
        scanner._match(f, '=')
        scanner._skip_white(f)
        _expression(f)
        codegen._store_primary_abs(label)


def _function(f):
    identifier = scanner._get_name(f)
    if identifier in _symtab:
        # Eventually calls sys.exit()
        error._error("Duplicate symbol function: " + str(identifier))
    scanner._match(f, '(')
    # Do something with parameter list
    scanner._match(f, ')')
    scanner._match(f, '{')
    _block(f)
    scanner._match(f, '}')


def _block(f):
    while scanner._nchar != '}':
        pass


def _expression(f):
    _term(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._or_ops:
            # Unget the op chars and reset scanner._nchar
            f.seek(-len(op) - 1, 1)
            scanner._nchar = f.read(1).decode("utf-8")
            # Break out of the loop - not our operator
            break
        codegen._push_primary()
        _term(f)
        codegen._pop_secondary()
        # Both branches use the same arguments
        regs = (codegen.PRIMARY, codegen.PRIMARY, codegen.SECONDARY)
        if op == '|':
            # Unpack the regs tuple as args
            codegen._bitwise_or(*regs)
        elif op == '||':
            codegen._logical_or(*regs)
        else:
            error._expected('| or ||')
        op = scanner._get_operator(f)


def _term(f):
    _factor(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._and_ops:
            # Unget the op chars and reset scanner._nchar
            f.seek(-len(op) - 1, 1)
            scanner._nchar = f.read(1).decode("utf-8")
            # Break out of the loop - not our operator
            break
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
        # Unget the op chars and reset scanner._nchar
        f.seek(-len(op) - 1, 1)
        scanner._nchar = f.read(1).decode("utf-8")


def _relation(f):
    _a_expression(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._rel_ops:
            # Unget the op chars and reset scanner._nchar
            f.seek(-len(op) - 1, 1)
            scanner._nchar = f.read(1).decode("utf-8")
            # Break out of the loop - not our operator
            break
        _a_expression(f)
        op = scanner._get_operator(f)


def _a_expression(f):
    _a_term(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._add_ops:
            # Unget the op chars and reset scanner._nchar
            f.seek(-len(op) - 1, 1)
            scanner._nchar = f.read(1).decode("utf-8")
            # Break out of the loop - not our operator
            break
        _a_term(f)
        op = scanner._get_operator(f)


def _a_term(f):
    _a_factor(f)
    op = scanner._get_operator(f)
    while op != "":
        if op not in scanner._mul_ops:
            # Unget the op chars and reset scanner._nchar
            f.seek(-len(op) - 1, 1)
            scanner._nchar = f.read(1).decode("utf-8")
            # Break out of the loop - not our operator
            break
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
        if scanner._nchar == '(':
            scanner._match(f, '(')
            _expression(f)
            scanner._match(f, ')')
        elif scanner._is_valid_identifier_start(scanner._nchar):
            id = scanner._get_name(f)
            # Do something with the identifier (push value to tos?)
            # TODO: determine if var or function
        elif scanner._is_num(scanner._nchar):
            n = scanner._get_num(f)
            codegen._load_primary_address(n)
    else:
        # Unget the op chars and reset scanner._nchar
        f.seek(-len(op), 1)
        scanner._nchar = f.read(1).decode("utf-8")


def _next_label():
    global _label_count
    label = _label_count
    _label_count += 1
    return label
