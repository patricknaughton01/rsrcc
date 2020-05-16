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
# Leave one word of space for our return address before storing local vars
_init_local_offset = -codegen.WORD // codegen.BYTE
_local_offset = _init_local_offset


def _program(f):
    name = scanner._get_name(f)
    while name == 'var':
        _global_var(f)
        name = scanner._get_name(f)
    # After parsing all the global variable declarations we want to jump to
    # main
    codegen._load_primary_address_relative(MAIN_LABEL)
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
    # Offset from base pointer for the local variables, leave one space for
    # pointer to the parent's bp
    offset = (codegen.WORD // codegen.BYTE)
    # Set local offset to track location of local variables.
    _local_offset = _init_local_offset
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
    # Function assembly body starts here
    # Save return address
    codegen._push_ret()
    _block(f)
    scanner._match(f, '}')
    # Remove our local symbol table
    _symtab.pop()


def _block(f):
    _symtab.append({})
    scanner._skip_white(f)
    local_allocations = 0
    dealloc = True
    while scanner._nchar != '}':
        identifier = scanner._get_name(f)
        if identifier == 'if':
            _if(f)
        elif identifier == 'while':
            _while(f)
        elif identifier == 'var':
            local_allocations += 1
            _local_var(f)
        elif identifier == 'break':
            pass
        elif identifier == 'return':
            dealloc = False
            # Dealloc local vars - special case because the code will exit
            # the block before the "end"
            codegen._dealloc_stack(local_allocations
                                   * codegen.WORD // codegen.BYTE)
            _return(f)
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
        scanner._skip_white(f)
    if dealloc:
        # Dealloc local vars to get back to return address
        codegen._dealloc_stack(local_allocations
                               * codegen.WORD // codegen.BYTE)
    _symtab.pop()


def _if(f):
    scanner._match(f, '(')
    _expression(f)
    scanner._match(f, ')')
    scanner._match(f, '{')
    label = LABEL_PREFIX + str(_next_label())
    codegen._load_branch_address_relative(label)
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
    codegen._load_branch_address_relative(label_exit)
    codegen._brzr_def()
    _block(f)
    codegen._load_branch_address_relative(label_loop)
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
    codegen._alloc_stack(num_param * codegen.WORD // codegen.BYTE)
    offset = codegen.WORD // codegen.BYTE
    scanner._match(f, '(')
    for i in range(num_param):
        _expression(f)
        codegen._store_primary(offset, codegen.STACK)
        offset += codegen.WORD // codegen.BYTE
        scanner._skip_white(f)
        if scanner._nchar == ',':
            scanner._match(f, ',')
        else:
            break
    scanner._match(f, ')')
    codegen._push(codegen.BASE)
    # Base pointer points to the thing that was just pushed (address of old
    # bp) and we need to offset b/c STACK points off end of stack
    codegen._load_address(codegen.BASE, codegen.STACK, codegen.WORD //
                          codegen.BYTE)
    codegen._load_branch_address_relative(entry['offset'])
    codegen._brl_def()
    # Clean up the stack: restore rb and remove the args we pushed
    codegen._pop(codegen.BASE)
    codegen._dealloc_stack(num_param * codegen.WORD // codegen.BYTE)


def _return(f):
    scanner._skip_white(f)
    if scanner._nchar == '(':
        scanner._match(f, '(')
        _expression(f)
        # Copy value over to return value register
        codegen._load_address(codegen.RETURN_VAL, codegen.PRIMARY, 0)
        scanner._match(f, ')')
    # Pop the return address into the BRANCH_TARGET register and return to it
    codegen._pop(codegen.BRANCH_TARGET)
    codegen._br_def()


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
            elif entry['type'] == 'function':
                _function_call(f, entry)
                # Move return value to primary
                codegen._load_primary_address(codegen.RETURN_VAL, 0)
            else:
                error._error("Unknown type of entry: {}".format(str(entry)))
        elif scanner._is_num(scanner._nchar):
            n = scanner._get_num(f)
            codegen._load_primary_address_relative(n)
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
