#!/usr/bin/env python

import sys
from pprint import pprint


def add_symbol(name, value=None):
    global symbols
    global first_available_symbol

    if value is None:
        value = first_available_symbol
        first_available_symbol += 1

    symbols[name] = value

    return value


def encode_acommand(command):
    label = command[1:]
    value = ""

    try:
        value = int(label)
    except ValueError:
        if label in symbols:
            value = symbols[label]
        else:
            value = add_symbol(label)

    binary = bin(value)[2:]  # Remove the '0b'
    return binary.rjust(16, "0")


def encode_ccommand(command):
    if "=" in command:
        dest, command_jump = command.split("=")
    else:
        dest = ""
        command_jump = command

    if ";" in command_jump:
        command, jump = command_jump.split(";")
    else:
        command = command_jump
        jump = ""

    dest_code = "{}{}{}".format(
        1 if "A" in dest else 0, 1 if "D" in dest else 0, 1 if "M" in dest else 0
    )
    jump_code = encode_jump(jump)
    comp_code = encode_comp(command)

    return "111{}{}{}".format(comp_code, dest_code, jump_code)


def encode_jump(jump):
    if jump == "JGT":
        return "001"
    elif jump == "JEQ":
        return "010"
    elif jump == "JGE":
        return "011"
    elif jump == "JLT":
        return "100"
    elif jump == "JNE":
        return "101"
    elif jump == "JLE":
        return "110"
    elif jump == "JMP":
        return "111"
    return "000"


def encode_comp(command):
    if command == "0":
        return "0101010"
    elif command == "1":
        return "0111111"
    elif command == "-1":
        return "0111010"
    elif command == "D":
        return "0001100"
    elif command == "A":
        return "0110000"
    elif command == "!D":
        return "0001111"
    elif command == "!A":
        return "0110001"
    elif command == "-D":
        return "0001111"
    elif command == "-A":
        return "0110011"
    elif command == "D+1":
        return "0011111"
    elif command == "A+1":
        return "0110111"
    elif command == "D-1":
        return "0001110"
    elif command == "A-1":
        return "0110010"
    elif command == "D+A":
        return "0000010"
    elif command == "D-A":
        return "0010011"
    elif command == "A-D":
        return "0000111"
    elif command == "D&A":
        return "0000000"
    elif command == "D|A":
        return "0010101"

    elif command == "M":
        return "1110000"
    elif command == "!M":
        return "1110001"
    elif command == "-M":
        return "1110011"
    elif command == "M+1":
        return "1110111"
    elif command == "M-1":
        return "1110010"
    elif command == "D+M":
        return "1000010"
    elif command == "D-M":
        return "1010011"
    elif command == "M-D":
        return "1000111"
    elif command == "D&M":
        return "1000000"
    elif command == "D|M":
        return "1010101"
    else:
        print("Cannot encode {}".format(command))
        sys.exit(1)


def main(file, outfile=None):
    with open(file, "r") as f:
        raw = f.readlines()

    content = []
    pos = 0

    for line in raw:
        without_comment = line.split("//", maxsplit=1)[0]
        without_space = without_comment.replace(" ", "")
        clean_line = without_comment.strip()
        if clean_line != "":
            if clean_line[0] == "(" and clean_line[-1] == ")":
                add_symbol(name=clean_line[1:-1], value=pos)
            else:
                content.append(clean_line)
                pos += 1
    asm = []
    for command in content:
        if command[0] == "@":
            # A-command
            asm.append("{}\n".format(encode_acommand(command)))
        else:
            # C-command
            asm.append("{}\n".format(encode_ccommand(command)))

    if not outfile:
        outfile = "{}.hack".format(file.split(".asm", 1)[0])

    with open(outfile, "w") as f:
        print("Write result in {}".format(outfile))
        f.writelines(asm)


symbols = {}
first_available_symbol = 16

add_symbol("SP", 0)
add_symbol("LCL", 1)
add_symbol("ARG", 2)
add_symbol("THIS", 3)
add_symbol("THAT", 4)
add_symbol("SCREEN", 0x4000)
add_symbol("KBD", 0x6000)
for i in range(16):
    add_symbol("R{}".format(i), i)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Must give an asm file as arg")
        sys.exit(1)
    main(file=sys.argv[1])
