"""Functions to generate assembly code. Retargeting to a
new architecture simply requires a change of the assembly output.
"""

PRIMARY = "r1"
SECONDARY = "r2"
ZERO = "r0"
STACK_REG = "r31"
BASE_REG = "r30"

def _alloc_global(label):
    # Allocate 1 32-bit word for the global and label this memory location
    print(label + ":\t.dw\t1")


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
    print("or {}, {}, {}".format(ra, rb, rc))


#################################################
# Stack Operations                              #
#################################################

def _pop_primary():
    _pop(PRIMARY)


def _pop_secondary():
    _pop(SECONDARY)


def _pop(reg):
    # Move SP first b/c it points off the end of the stack
    print("addi {}, {}, 4".format(STACK_REG, STACK_REG))
    _load(reg, 0, STACK_REG)


def _push_primary():
    _push(PRIMARY)


def _push_secondary():
    _push(SECONDARY)


def _push(reg):
    _store(reg, 0, STACK_REG)
    print("addi {}, {}, -4".format(STACK_REG, STACK_REG))


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
