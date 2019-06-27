// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

@R2
M=0

@R0
D=M // D = R0
@END
D;JEQ // goto END if R0 == 0

@R1
D=M // D = R0
@END
D;JEQ // goto END if R1 == 0

(LOOP)
@R2
D = M

@R1
D=D+M // D += R1

@R2
M = D

@R0
MD = M-1

@LOOP
D;JGT

(END)
@END
0;JMP
