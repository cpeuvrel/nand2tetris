#!/usr/bin/env python

import sys

#### RAM Usage
## 0-15: 16 virtual registers
## 16-255: static variables
## 256-2047: stack
## 2048-16483: heap
## 16384-24575: I/O

class VMEmulator:
    memory_segment = {
        'argument': {
            "start": 2,
            "size": 1
        },
        'local': {
            "start": 1,
            "size": 1
        },
        'static': {
            "start": 16,
            "size": 240
        },
        'constant': {
            "start": -1,
            "size": 32768
        },
        'this': {
            "start": 3,
            "size": 1
        },
        'that': {
            "start": 4,
            "size": 1
        },
        'pointer': {
            "start": 3,
            "size": 2
        },
        'temp': {
            "start": 5,
            "size": 10
        },
    }

    asm = []


    def encode_push(self, segment, index):
        if segment == 'constant':
            # // D = <cst>
            # @<cst> // A=<cst> / D=? / M=?
            # D=A    // A=<cst> / D=<cst> / M=?
            self.asm.append('@{}'.format(index)) # A = <cst>
            self.asm.append('D=A') # D = <cst>
        elif segment == 'static':
            # TODO
            print('does not support PUSH static yet')
            sys.exit(1)
        else:
            # // D = R[<segment + index = addr>] = <data>
            # @<addr> // A=<addr> / D=? / M=<data>
            # D=M     // A=<addr> / D=<data> / M=<data>
            address = self.memory_segment[segment]['start'] + index
            self.asm.append('@{}'.format(address)) # A = <addr>
            self.asm.append('D=M') # D = <data>

        # // R[R[SP]] = D
        # @SP     // A=SP / D=<data>  / M=R[SP]
        # A=M     // A=R[SP] / D=<data> / M=R[R[SP]]
        # M=D     // A=R[SP] / D=<data> / M=R[R[SP]]=<data>
        self.asm.append('@SP') # A = SP
        self.asm.append('A=M') # M= R[R[SP]]
        self.asm.append('M=D') # M= R[R[SP]] = <data>

        self.incr_sp()


    def encode_pop(self, segment, index):
        self.decr_sp()

        # // D = R[R[SP]]
        # @SP     // A=SP / D=?  / M=R[SP]
        # A=M     // A=R[SP] / D=? / M=R[R[SP]]=<data>
        # D=M     // A=R[SP] / D=<data> / M=R[R[SP]]
        self.asm.append('@SP') # A = SP
        self.asm.append('A=M') # M= R[R[SP]] (= <data>)
        self.asm.append('D=M') # D= R[R[SP]] 

        # // R[<addr>] = D
        # @<addr> // A=<addr> / D=<data> / M=?
        # D=M     // A=<addr> / D=<data> / M=<data>
        address = self.memory_segment[segment]['start'] + index
        self.asm.append('@{}'.format(address)) # A = <addr>
        self.asm.append('M=D') # M = <data>

    def prepare_logic_arithmetic_binary(self):
        # A,D,M registers unknown. Starting Stack :
        # a
        # b
        # c
        #    <- SP

        # This function will put `c` in `D` register, `b` in `M` register and decrement SP twice
        # D=c, M=b, A=SP
        # Final Stack :
        # a
        # b  <- SP
        # c

        self.decr_sp()

        # // D = R[R[SP]] = <arg1>
        self.asm.append('@SP') # A = SP
        self.asm.append('A=M') # M= R[R[SP]] (=<arg1>)
        self.asm.append('D=M') # D= R[R[SP]] 

        self.decr_sp()

        # // M = R[R[SP]](=<arg2>)
        self.asm.append('@SP') # A = SP
        self.asm.append('A=M') # M= R[R[SP]] (=<arg2>)


    def encode_add(self):
        self.prepare_logic_arithmetic_binary()

        # // M = D+M
        self.asm.append('M=D+M') # D= <arg1> + <arg2>
        self.incr_sp()


    def decr_sp(self):
        # Decrement SP register
        # Does not touch `D` register
        self.asm.append('@SP') # A=SP
        self.asm.append('M=M-1') # R[SP]--

    def incr_sp(self):
        # Increment SP register
        # Does not touch `D` register
        self.asm.append('@SP') # A=SP
        self.asm.append('M=M+1') # R[SP]--

    def main(self, file, outfile=None):
        with open(file, "r") as f:
            raw = f.readlines()

        content = []

        for line in raw:
            without_comment = line.split("//", maxsplit=1)[0]
            clean_line = without_comment.strip()
            if clean_line != "":
                content.append(clean_line)

        for line in content:
            line_parsed = line.split(" ")
            command = line_parsed[0]
            arg1 = None if len(line_parsed) < 2 else line_parsed[1]
            arg2 = None if len(line_parsed) < 3 else line_parsed[2]

            if command == "push":
                self.encode_push(arg1, arg2)
            elif command == "pop":
                self.encode_pop(arg1, arg2)
            elif command == "add":
                self.encode_add()

        if not outfile:
            outfile = "{}.self.asm".format(file.split(".vm", 1)[0])

        with open(outfile, "w") as f:
            print("Write result in {}".format(outfile))
            f.writelines(['{}\n'.format(line) for line in self.asm])

if __name__ == "__main__":
    # TODO: handle give a directory with several vm
    if len(sys.argv) != 2:
        print("Must give a vm file as arg")
        sys.exit(1)

    VMEmulator().main(file=sys.argv[1])
