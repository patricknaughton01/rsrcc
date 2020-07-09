lar r31, 65528
lar r30, 65532
GL0:	.dw	1
GL1:	.dw	1
lar r1, MAIN
br r1
F_fib2:	
st r18, 0(r31)
addi r31, r31, -4
ld r1, 4(r30)
st r1, 0(r31)
addi r31, r31, -4
lar r1, 2
addi r31, r31, 4
ld r2, 0(r31)
sub r1, r2, r1
shra r1, r1, 31
lar r3, L3
brzr r3, r1
addi r31, r31, 0
ld r1, 4(r30)
la r19, 0(r1)
addi r31, r31, 4
ld r3, 0(r31)
br r3
L3:	
addi r31, r31, 0
addi r31, r31, -4
ld r1, 4(r30)
st r1, 0(r31)
addi r31, r31, -4
lar r1, 1
addi r31, r31, 4
ld r2, 0(r31)
sub r1, r2, r1
st r1, 4(r31)
st r30, 0(r31)
addi r31, r31, -4
la r30, 4(r31)
lar r3, F_fib2
brl r18, r3
addi r31, r31, 4
ld r30, 0(r31)
addi r31, r31, 4
la r1, 0(r19)
st r1, 0(r31)
addi r31, r31, -4
addi r31, r31, -4
ld r1, 4(r30)
st r1, 0(r31)
addi r31, r31, -4
lar r1, 2
addi r31, r31, 4
ld r2, 0(r31)
sub r1, r2, r1
st r1, 4(r31)
st r30, 0(r31)
addi r31, r31, -4
la r30, 4(r31)
lar r3, F_fib2
brl r18, r3
addi r31, r31, 4
ld r30, 0(r31)
addi r31, r31, 4
la r1, 0(r19)
addi r31, r31, 4
ld r2, 0(r31)
add r1, r2, r1
la r19, 0(r1)
addi r31, r31, 4
ld r3, 0(r31)
br r3
F_swap4:	
st r18, 0(r31)
addi r31, r31, -4
addi r31, r31, -4
ld r1, 4(r30)
ld r1, 0(r1)
st r1, -8(r30)
ld r1, 4(r30)
st r1, 0(r31)
addi r31, r31, -4
ld r1, 8(r30)
ld r1, 0(r1)
addi r31, r31, 4
ld r2, 0(r31)
st r1, 0(r2)
ld r1, 8(r30)
st r1, 0(r31)
addi r31, r31, -4
ld r1, -8(r30)
addi r31, r31, 4
ld r2, 0(r31)
st r1, 0(r2)
addi r31, r31, 4
addi r31, r31, 4
ld r3, 0(r31)
br r3
MAIN:	
st r18, 0(r31)
addi r31, r31, -4
addi r31, r31, -4
lar r1, 1
st r1, 4(r31)
st r30, 0(r31)
addi r31, r31, -4
la r30, 4(r31)
lar r3, F_fib2
brl r18, r3
addi r31, r31, 4
ld r30, 0(r31)
addi r31, r31, 4
la r1, 0(r19)
st r1, GL0(r0)
addi r31, r31, -4
lar r1, 5
st r1, 4(r31)
st r30, 0(r31)
addi r31, r31, -4
la r30, 4(r31)
lar r3, F_fib2
brl r18, r3
addi r31, r31, 4
ld r30, 0(r31)
addi r31, r31, 4
la r1, 0(r19)
st r1, GL1(r0)
addi r31, r31, -4
lar r1, 65280
st r1, -8(r30)
addi r31, r31, -4
lar r1, 65284
st r1, -12(r30)
ld r1, -8(r30)
st r1, 0(r31)
addi r31, r31, -4
lar r1, 1
addi r31, r31, 4
ld r2, 0(r31)
st r1, 0(r2)
ld r1, -12(r30)
st r1, 0(r31)
addi r31, r31, -4
lar r1, 2
addi r31, r31, 4
ld r2, 0(r31)
st r1, 0(r2)
addi r31, r31, -8
ld r1, -8(r30)
st r1, 4(r31)
ld r1, -12(r30)
st r1, 8(r31)
st r30, 0(r31)
addi r31, r31, -4
la r30, 4(r31)
lar r3, F_swap4
brl r18, r3
addi r31, r31, 4
ld r30, 0(r31)
addi r31, r31, 8
addi r31, r31, 8
stop
END
