"""Parser for the program to convert tokens into object code.
"""

import error
import codegen
import scanner

GLOBAL_PREFIX = "GL"
FUNCTION_PREFIX = "F"
LABEL_PREFIX = "L"
MAIN = "main"
MAIN_LABEL = "MAIN"

_keywords = {'if', 'else', 'while', 'function', 'var', 'return'}
# Really a stack of symbol tables so that we can track different scopes
# `_symtab[0]` is the global symbol table
_symtab = [{}]
_label_count = 0
_local_offset = 0


def _program(f):
    name = scanner._get_name(f)
    while name == 'var':
        _global_var(f)
        name = scanner._get_name(f)
    # After parsing all the global variable declarations we want to jump to
    # main
    codegen._load_primary_address(MAIN_LABEL)
    codegen._br(codegen.PRIMARY)
    while name == 'function':
        _function(f)
        name = scanner._get_name(f)


def _global_var(f):
    global _symtab, _keywords
    identifier = scanner._get_name(f)
    scanner._skip_white(f)
    if identifier in _symtab[0]:
        # Eventually calls sys.exit()
        error._error("Duplicate symbol variable: " + str(identifier))
    if identifier in _keywords:
        error._error("Variable shadows keyword: " + str(identifier))
    label = GLOBAL_PREFIX + str(_next_label())
    codegen._alloc_global(label)
    _symtab[0][identifier] = {'type': 'global_var', 'offset': label, 'base':
        codegen.ZERO}
    if scanner._nchar == '=':
        # This variable is initialized
        scanner._match(f, '=')
        scanner._skip_white(f)
        _expression(f)
        codegen._store_primary_abs(label)


def _function(f):
    global _local_offset
    identifier = scanner._get_name(f)
    scanner._skip_white(f)
    if identifier in _symtab[0]:
        # Eventually calls sys.exit()
        error._error("Duplicate symbol function: " + str(identifier))
    _symtab[0][identifier] = {'type': 'function'}
    scanner._match(f, '(')
    # Offset from base pointer for the local variables, leave two spaces for
    # pointer to the parent's bp and the function's return address
    offset = (codegen.WORD // codegen.BYTE) * 2
    # Set local offset to track location of local variables.
    _local_offset = 0
    local_symbols = {}
    while scanner._is_valid_identifier_start(scanner._nchar):
        id = scanner._get_name(f)
        if id in local_symbols:
            error._error("Duplicate parameter: " + str(id))
        local_symbols[id] = {'type': 'local_var', 'offset': offset, 'base':
                             codegen.BASE}
        scanner._skip_white(f)
        if scanner._nchar == ',':
            scanner._match(f, ',')
            scanner._skip_white(f)
        else:
            # No more parameters to read
            break
        offset += codegen.WORD // codegen.BYTE
    _symtab[0][identifier]['num_param'] = len(local_symbols)
    # Add our local symbols so that descendant blocks can see them
    _symtab.append(local_symbols)
    scanner._match(f, ')')
    scanner._match(f, '{')
    if identifier == MAIN:
        label = MAIN_LABEL
    else:
        label = "{}_{}{}".format(FUNCTION_PREFIX, identifier, _next_label())
    _symtab[0][identifier]['offset'] = label
    _symtab[0][identifier]['base'] = codegen.ZERO
    codegen._post_label(label)
    _block(f)
    scanner._match(f, '}')
    # Remove our local symbol table
    _symtab.pop()


def _block(f):
    _symtab.append({})
    scanner._skip_white(f)
    while scanner._nchar != '}':
        identifier = scanner._get_name(f)
        if identifier == 'if':
            _if(f)
        elif identifier == 'while':
            _while(f)
        elif identifier == 'var':
            _local_var(f)
        elif identifier == 'break':
            pass
        else:
            # Either an assignment or a function call
            # Look in symbol table to tell which is which
            entry = _lookup(identifier)
            if entry is not None:
                if entry['type'] == 'local_var' or entry['type'] == \
                        'global_var':
                    _assignment(f, entry)
                elif entry['type'] == 'function':
                    _function_call(f, entry)
            else:
                error._error("Undeclared identifier: " + str(identifier))
    _symtab.pop()


def _if(f):
    scanner._match(f, '(')
    _expression(f)
    scanner._match(f, ')')
    scanner._match(f, '{')
    label = LABEL_PREFIX + str(_next_label())
    codegen._load_branch_address(label)
    codegen._brzr_def()
    _block(f)
    codegen._post_label(label)
    scanner._match(f, '}')
    scanner._skip_white(f)


def _while(f):
    label_loop, label_exit = LABEL_PREFIX + str(_next_label()), \
                             LABEL_PREFIX + str(_next_label())
    codegen._post_label(label_loop)
    scanner._match(f, '(')
    _expression(f)
    scanner._match(f, ')')
    scanner._match(f, '{')
    codegen._load_branch_address(label_exit)
    codegen._brzr_def()
    _block(f)
    codegen._load_branch_address(label_loop)
    codegen._br_def()
    scanner._match(f, '}')


def _local_var(f):
    global _local_offset
    _local_offset -= (codegen.WORD // codegen.BYTE)
    identifier = scanner._get_name(f)
    if identifier in _symtab[-1]:
        error._error("Repeat local identifier: " + str(identifier))
    _symtab[-1][identifier] = {'type': 'local_var', 'offset': _local_offset,
                               'base': codegen.BASE}
    # Allocate space for var on stack
    codegen._alloc_stack(codegen.WORD // codegen.BYTE)
    scanner._skip_white(f)
    if scanner._nchar == '=':
        scanner._match(f, '=')
        _expression(f)
        entry = _symtab[-1][identifier]
        codegen._store_primary(entry['offset'], entry['base'])


def _assignment(f, entry):
    scanner._match(f, '=')
    _expression(f)
    codegen._store_primary(entry['offset'], entry['base'])


def _function_call(f, entry):
    num_param = entry['num_param']



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
        codegen._push_primary()
        _factor(f)
        codegen._pop_secondary()
        regs = (codegen.PRIMARY, codegen.PRIMARY, codegen.SECONDARY)
        if op == '&':
            codegen._bitwise_and(*regs)
        elif op == '&&':
            codegen._logical_and(*regs)
        else:
            error._expected('& or &&')
        op = scanner._get_operator(f)


def _factor(f):
    op = scanner._get_operator(f)
    if op in scanner._not_ops:
        _factor(f)
        regs = (codegen.PRIMARY, codegen.PRIMARY)
        if op == '~':
            codegen._bitwise_not(*regs)
        elif op == '!':
            codegen._logical_not(*regs)
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
        codegen._push_primary()
        _a_expression(f)
        codegen._pop_secondary()
        codegen._cmp_def(op)
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
        # TODO Handle unary ++ and --
        codegen._push_primary()
        _a_term(f)
        codegen._pop_secondary()
        # Flip order of primary and secondary for - b/c second argument is
        # the one in primary. + is commutative so it doesn't matter for that
        # case
        regs = (codegen.PRIMARY, codegen.SECONDARY, codegen.PRIMARY)
        if op == '+':
            codegen._add(*regs)
        elif op == '-':
            codegen._sub(*regs)
        else:
            error._expected('+ or -')
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
        codegen._push_primary()
        _a_factor(f)
        codegen._pop_secondary()
        # Flip order for / for same reason as -. * is comm so doesn't matter
        regs = (codegen.PRIMARY, codegen.SECONDARY, codegen.PRIMARY)
        if op == '*':
            codegen._mul(*regs)
        elif op == '/':
            codegen._div(*regs)
        else:
            error._expected('* or /')
        op = scanner._get_operator(f)


def _a_factor(f):
    op = scanner._get_operator(f)
    if op in scanner._add_ops:
        _a_factor(f)
        if op == '-':
            # Negate the primary reg, if + we don't have to do anything
            codegen._neg(codegen.PRIMARY, codegen.PRIMARY)
    elif op == '':
        if scanner._nchar == '(':
            scanner._match(f, '(')
            _expression(f)
            scanner._match(f, ')')
        elif scanner._is_valid_identifier_start(scanner._nchar):
            id = scanner._get_name(f)
            entry = _lookup(id)
            if entry is None:
                error._error("Undeclared identifier: " + str(id))
            if entry['type'] == 'global_var' or entry['type'] == 'local_var':
                codegen._load_primary(entry['offset'], entry['base'])
            # TODO handle function calls
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


def _lookup(symbol):
    # Search symbol tables in reverse order so that we find the symbol with
    # this name in the narrowest scope
    for i in range(len(_symtab)-1, -1, -1):
        if symbol in _symtab[i]:
            return _symtab[i][symbol]
    return None
