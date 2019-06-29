#!/usr/bin/env python

import sys
import re

## TODO: optimize all `@SP` when `A` already == `SP`

#### RAM Usage
## 0-15: 16 virtual registers
## 16-255: static variables
## 256-2047: stack
## 2048-16483: heap
## 16384-24575: I/O


class VMEmulator:
    memory_segment = {
        "argument": {"start": 2, "size": 1},
        "local": {"start": 1, "size": 1},
        "static": {"start": 16, "size": 240},
        "constant": {"start": -1, "size": 32768},
        "this": {"start": 3, "size": 1},
        "that": {"start": 4, "size": 1},
        "pointer": {"start": 3, "size": 2},
        "temp": {"start": 5, "size": 10},
    }

    asm = []
    filename = ""
    lineno = 0

    function_stack = ["Sys.init"]
    local_var_count_by_function = {}

    def current_function(self):
        return self.function_stack[-1]

    def decr_sp(self):
        # Decrement SP register
        # Does not touch `D` register
        self.asm.append("@SP")  # A=SP
        self.asm.append("M=M-1")  # R[SP]--

    def incr_sp(self):
        # Increment SP register
        # Does not touch `D` register
        self.asm.append("@SP")  # A=SP
        self.asm.append("M=M+1")  # R[SP]--

    def pop_stack_in_d(self):
        self.decr_sp()

        # // D = R[R[SP]]
        # @SP     // A=SP / D=?  / M=R[SP]
        # A=M     // A=R[SP] / D=? / M=R[R[SP]]=<data>
        # D=M     // A=R[SP] / D=<data> / M=R[R[SP]]
        self.asm.append("@SP")  # A = SP
        self.asm.append("A=M")  # M= R[R[SP]] (= <data>)
        self.asm.append("D=M")  # D= R[R[SP]]

    def encode_push(self, segment, index):
        if segment == "constant":
            # // D = <cst>
            # @<cst> // A=<cst> / D=? / M=?
            # D=A    // A=<cst> / D=<cst> / M=?
            self.asm.append("@{}".format(index))  # A = <cst>
            self.asm.append("D=A")  # D = <cst>
        elif segment == "static":
            self.asm.append("@{}_{}".format(self.filename, index))  # A = <cst>
            self.asm.append("D=M")  # D = <cst>
        else:
            # // R[5] = <base addr> + <index>
            address = self.memory_segment[segment]["start"]
            self.asm.append("@{}".format(address))  # A = <base addr>
            # if segment != 'temp':
            if segment != "temp" and segment != "pointer":
                self.asm.append("A=M")
            self.asm.append("D=A")
            self.asm.append("@{}".format(index))  # A = <base addr>
            self.asm.append("A=D+A")

            # // D = R[<segment + index = addr>] = <data>
            # @<addr> // A=<addr> / D=? / M=<data>
            # D=M     // A=<addr> / D=<data> / M=<data>
            self.asm.append("D=M")  # D = <data>

        # // R[R[SP]] = D
        # @SP     // A=SP / D=<data>  / M=R[SP]
        # A=M     // A=R[SP] / D=<data> / M=R[R[SP]]
        # M=D     // A=R[SP] / D=<data> / M=R[R[SP]]=<data>
        self.asm.append("@SP")  # A = SP
        self.asm.append("A=M")  # M= R[R[SP]]
        self.asm.append("M=D")  # M= R[R[SP]] = <data>

        self.incr_sp()

    def encode_pop(self, segment, index):
        # Use R5 as temporary register for storing the dst address
        if segment == "static":
            self.asm.append("@{}_{}".format(self.filename, index))  # A = <cst>
            self.asm.append("D=M")  # D = <cst>
        else:
            # // R[5] = <base addr> + <index>
            address = self.memory_segment[segment]["start"]
            self.asm.append("@{}".format(address))  # A = <base addr>
            if segment != "temp" and segment != "pointer":
                self.asm.append("A=M")
            self.asm.append("D=A")
            self.asm.append("@{}".format(index))  # A = <index>
            self.asm.append("D=D+A")

        self.asm.append("@5")
        self.asm.append("M=D")

        self.pop_stack_in_d()

        # // R[<addr>] = D
        # @<addr> // A=<addr> / D=<data> / M=?
        # D=M     // A=<addr> / D=<data> / M=<data>
        self.asm.append("@5")
        self.asm.append("A=M")
        self.asm.append("M=D")  # M = <data>

    def prepare_logic_arithmetic_unary(self):
        # A,D,M registers unknown. Starting Stack :
        # a
        # b
        # c
        #    <- SP

        # This function will put `c` in `M` register and decrement SP
        # D=?, M=c, A=SP
        # Final Stack :
        # a
        # b
        # c  <- SP

        self.decr_sp()

        # // D = R[R[SP]] = <arg1>
        self.asm.append("@SP")  # A = SP
        self.asm.append("A=M")  # M= R[R[SP]] (=<arg1>)

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

        self.prepare_logic_arithmetic_unary()
        self.asm.append("D=M")  # D= R[R[SP]]
        self.decr_sp()

        # // M = R[R[SP]](=<arg2>)
        self.asm.append("@SP")  # A = SP
        self.asm.append("A=M")  # M= R[R[SP]] (=<arg2>)

    def normalize_filepath(self, path):
        return re.sub("[^A-Za-z0-9]", "_", path)

    def compare(self, test_op):
        ## Set R[R[SP]] = 0/-1 depending on the test success
        label_base = "{}_{}".format(self.normalize_filepath(self.filename), self.lineno)

        ## Set D=-1 if test is true, else D=0
        self.asm.append("@{}_true".format(label_base))
        self.asm.append("D;{}".format(test_op))
        self.asm.append("@{}_false".format(label_base))
        self.asm.append("0;JMP")

        self.asm.append("({}_true)".format(label_base))
        self.asm.append("D=-1")

        self.asm.append("@{}_end".format(label_base))
        self.asm.append("0;JMP")

        self.asm.append("({}_false)".format(label_base))
        self.asm.append("D=0")

        self.asm.append("({}_end)".format(label_base))

        ## Set R[R[SP]] = D
        self.asm.append("@SP")
        self.asm.append("A=M")
        self.asm.append("M=D")

    def encode_add(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("M=D+M")  # D= <arg1> + <arg2>
        self.incr_sp()

    def encode_sub(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("M=M-D")  # D= <arg2> - <arg1>
        self.incr_sp()

    def encode_and(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("M=D&M")  # D= <arg1> & <arg2>
        self.incr_sp()

    def encode_or(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("M=D|M")  # D= <arg1> | <arg2>
        self.incr_sp()

    def encode_neg(self):
        self.prepare_logic_arithmetic_unary()
        self.asm.append("M=-M")  # D= - <arg1>
        self.incr_sp()

    def encode_not(self):
        self.prepare_logic_arithmetic_unary()
        self.asm.append("M=!M")  # D= - <arg1>
        self.incr_sp()

    def encode_eq(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("D=M-D")  # D= <arg1> - <arg2>
        self.compare("JEQ")
        self.incr_sp()

    def encode_gt(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("D=M-D")  # D= <arg1> - <arg2>
        self.compare("JGT")
        self.incr_sp()

    def encode_lt(self):
        self.prepare_logic_arithmetic_binary()
        self.asm.append("D=M-D")  # D= <arg1> - <arg2>
        self.compare("JLT")
        self.incr_sp()

    def encode_label(self, label):
        self.asm.append("({}:{})".format(self.current_function(), label))

    def encode_goto(self, label):
        self.asm.append("@{}:{}".format(self.current_function(), label))
        self.asm.append("0;JMP")

    def encode_ifgoto(self, label):
        self.pop_stack_in_d()
        self.asm.append("@{}:{}".format(self.current_function(), label))
        self.asm.append("D;JNE")

    def encode_call(self, function_name, arg_count):
        # Save return address and the segment pointers
        # Set local and argument segments
        # Transfer control to called function
        pass

    def encode_function(self, function_name, local_var_count):
        self.asm.append("({})".format(function_name))
        self.function_stack.append(function_name)
        self.local_var_count_by_function[function_name] = local_var_count

        for i in range(int(local_var_count)):
            # Allocate and init 0 all local variables
            self.asm.append("@SP")
            self.asm.append("A=M")
            self.asm.append("M=0")
            self.incr_sp()

    def encode_return(self):
        # Keep last value in stack in D (temporarly stored in R[6] == temp 1)
        self.pop_stack_in_d()
        self.asm.append("@6")
        self.asm.append("M=D")

        # Clear arg&garbage from the stack
        self.asm.append("@LCL")
        self.asm.append("D=M")
        self.asm.append("@SP")
        self.asm.append("M=D")

        def restore_field(field):
            self.pop_stack_in_d()
            self.asm.append("@{}".format(field))
            self.asm.append("M=D")

        # Restore local, arg, this, that segments of the calling function
        restore_field("THAT")
        restore_field("THIS")
        restore_field("ARG")
        restore_field("LCL")

        # Store retrun address
        self.pop_stack_in_d()
        self.asm.append("@SP")
        for arg in range(int(self.local_var_count_by_function[self.current_function()])):
            self.asm.append("M=M-1")

        # Push back to the stack the stored value
        self.encode_push('temp', 1)

        # Jump to retrun address
        self.asm.append("A=D")
        self.asm.append("0;JMP")
        self.function_stack.pop()

    def main(self, file, outfile=None):
        self.filename = file
        self.lineno = 0
        with open(file, "r") as f:
            raw = f.readlines()

        content = []

        for line in raw:
            without_comment = line.split("//", maxsplit=1)[0]
            clean_line = without_comment.strip()
            if clean_line != "":
                content.append(clean_line)

        for line in content:
            self.lineno += 1

            self.asm.append("// {}".format(line))
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
            elif command == "sub":
                self.encode_sub()
            elif command == "and":
                self.encode_and()
            elif command == "or":
                self.encode_or()
            elif command == "neg":
                self.encode_neg()
            elif command == "not":
                self.encode_not()
            elif command == "eq":
                self.encode_eq()
            elif command == "gt":
                self.encode_gt()
            elif command == "lt":
                self.encode_lt()
            elif command == "label":
                self.encode_label(arg1)
            elif command == "goto":
                self.encode_goto(arg1)
            elif command == "if-goto":
                self.encode_ifgoto(arg1)
            elif command == "function":
                self.encode_function(arg1, arg2)
            elif command == "return":
                 self.encode_return()
            else:
                print("Unknown command: {}".format(command))

        if not outfile:
            outfile = "{}.asm".format(file.split(".vm", 1)[0])

        with open(outfile, "w") as f:
            print("Write result in {}".format(outfile))
            f.writelines(["{}\n".format(line) for line in self.asm])


if __name__ == "__main__":
    # TODO: handle give a directory with several vm
    if len(sys.argv) != 2:
        print("Must give a vm file as arg")
        sys.exit(1)

    VMEmulator().main(file=sys.argv[1])
