"""Functions to generate assembly code. Retargeting to a
new architecture simply requires a change of the assembly output.
"""

PRIMARY = "r1"
SECONDARY = "r2"
STATUS = PRIMARY    # Put statuses from comparision results in the PRIMARY reg
ZERO = "r0"
STACK_REG = "r31"
BASE_REG = "r30"
WORD = 32
BYTE = 8


def _alloc_global(label):
    # Allocate 1 32-bit word for the global and label this memory location
    print(label + ":\t.dw\t1")


#################################################
# Comp Operations                               #
#################################################

def _cmp_def(op):
    _cmp(STATUS, PRIMARY, SECONDARY, op)


def _cmp(ra, rb, rc, op):
    """Compare rb and rc using the operator op. Put the result in ra. If
    the comparision is true, ra will be non zero, otherwise it will be zero
    """
    _sub(ra, rb, rc)
    # Note that we don't have to do anything extra for `!=` because the
    # subtraction handles that for us
    if op == '<' or op == '>=':
        # In both cases, we just need to check the sign bit
        # For <, true if sign bit is set (rb-rc < 0)
        _shra(ra, ra, WORD-1)
        if op == '>=':
            # true if sign bit is cleared, to comply with interface, need to
            # not the result
            _bitwise_not(ra, ra)
    elif op == '>' or op == '<=':
        # For >, rb-rc is strictly positive so its negative is strictly
        # negative, then we just check the sign (-0 = 0 so the sign will
        # still be 0)
        _neg(ra, ra)
        _shra(ra, ra, WORD-1)
        if op == '<=':
            _bitwise_not(ra, ra)
    elif op == '==':
        _bitwise_not(ra, ra)


#################################################
# Arith Operations                              #
#################################################

def _bitwise_or(ra, rb, rc):
    """Bitwise or rb and rc and put result in ra
    """
    print("or {}, {}, {}".format(ra, rb, rc))


def _logical_or(ra, rb, rc):
    """Logical or rb and rc and put result in ra
    Right now, there is no instruction for logical or so this just does the
    same thing as `_bitwise_or`
    """
    print("lor {}, {}, {}".format(ra, rb, rc))


def _bitwise_and(ra, rb, rc):
    """Bitwise and rb and rc and put result in ra
    """
    print("and {}, {}, {}".format(ra, rb, rc))


def _logical_and(ra, rb, rc):
    """Logical and rb and rc and put result in ra
    Right now, there is no instruction for logical and so this just does the
    same thing as `_bitwise_and`
    """
    print("land {}, {}, {}".format(ra, rb, rc))


def _bitwise_not(ra, rc):
    """Bitwise not rc and put result in ra
    """
    print("not {}, {}".format(ra, rc))


def _logical_not(ra, rc):
    """Logical not rc and put result in ra
    Right now, there is no instruction for logical not so this just does the
    same thing as `_bitwise_not`
    """
    print("lnot {}, {}".format(ra, rc))


def _add(ra, rb, rc):
    print("add {}, {}, {}".format(ra, rb, rc))


def _addi(ra, rb, c):
    print("addi {}, {}, {}".format(ra, rb, c))


def _sub(ra, rb, rc):
    print("sub {}, {}, {}".format(ra, rb, rc))


def _neg(ra, rc):
    print("neg {}, {}".format(ra, rc))


def _mul(ra, rb, rc):
    print("mul {}, {}, {}".format(ra, rb, rc))


def _div(ra, rb, rc):
    print("div {}, {}, {}".format(ra, rb, rc))


def _shr(ra, rb, r_c):
    """Shift rb right (logically) by either register rc or constant c and put
    result in ra
    """
    print("shr {}, {}, {}".format(ra, rb, r_c))


def _shra(ra, rb, r_c):
    """Shift rb right (arithmetically, i.e., sign extend) by either register
    rc or constant c and put result in ra
    """
    print("shra {}, {}, {}".format(ra, rb, r_c))


def _shl(ra, rb, r_c):
    """Shift rb left (logically) by either register rc or constant c and put
    result in ra
    """
    print("shl {}, {}, {}".format(ra, rb, r_c))


#################################################
# Stack Operations                              #
#################################################

def _pop_primary():
    _pop(PRIMARY)


def _pop_secondary():
    _pop(SECONDARY)


def _pop(reg):
    # Move SP first b/c it points off the end of the stack
    _addi(STACK_REG, STACK_REG, WORD / BYTE)
    _load(reg, 0, STACK_REG)


def _push_primary():
    _push(PRIMARY)


def _push_secondary():
    _push(SECONDARY)


def _push(reg):
    _store(reg, 0, STACK_REG)
    _addi(STACK_REG, STACK_REG, -WORD / BYTE)


#################################################
# LD/ST Operations                              #
#################################################

def _load_primary_address(addr):
    _load_address(PRIMARY, addr)


def _load_address(reg, addr):
    print("lar {}, {}".format(reg, addr))


def _load_primary_abs(offset):
    _load_primary(offset, ZERO)


def _load_primary(offset, base):
    _load(PRIMARY, offset, base)


def _load_abs(reg, offset):
    _load(reg, offset, ZERO)


def _load(reg, offset, base):
    print("ld {}, {}({})".format(reg, offset, base))


def _store_primary_abs(offset):
    _store_primary(offset, ZERO)


def _store_primary(offset, base):
    _store(PRIMARY, offset, base)


def _store_abs(reg, offset):
    _store(reg, offset, ZERO)


def _store(reg, offset, base):
    print("st {}, {}({})".format(reg, offset, base))


#################################################
# PostLabel                                     #
#################################################

def _post_label(label):
    print("{}:\t".format(label))
