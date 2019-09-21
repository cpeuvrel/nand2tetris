#!/usr/bin/env python

import sys
import os

from compiler.jack_compiler import JackCompiler
from compiler.jack_tokenizer import JackTokenizer

class Compiler:
    filename = ""
    def __init__(self, filename):
        self.filename = filename

    def main(self, opts):
        debug = "--debug" in opts

        if os.path.isdir(self.filename):
            # Remove trailing slash
            if self.filename.endswith("/"):
                self.filename = self.filename[:-1]

            for dir_file in os.listdir(self.filename):
                abs_path = '{}/{}'.format(self.filename, dir_file)
                if os.path.isfile(abs_path) and dir_file.endswith('.jack'):
                    print("Parse {}".format(abs_path))
                    self.compile_file(abs_path, debug)
        else:
            self.compile_file(self.filename, debug)

    @staticmethod
    def compile_file(file, debug=False):
        tokenizer = JackTokenizer()
        compiler = JackCompiler()

        tokenizer.tokenize_file(file)
        compiler.compile_ast(tokenizer.ast)

        outfile_token = "{}T.xml".format(file.split(".jack", 1)[0])
        outfile_parsed = "{}.xml".format(file.split(".jack", 1)[0])
        outfile_vm = "{}.vm".format(file.split(".jack", 1)[0])

        if debug:
            with open(outfile_token, "w") as f:
                print("Write tokens result in {}".format(outfile_token))
                f.writelines(["{}\n".format(line) for line in tokenizer.tokens_xml])

            with open(outfile_parsed, "w") as f:
                print("Write parsed result in {}".format(outfile_parsed))
                f.writelines(["{}\n".format(line) for line in tokenizer.parsed_xml])

        with open(outfile_vm, "w") as f:
            print("Write vm result in {}".format(outfile_vm))
            f.writelines(["{}\n".format(line) for line in compiler.vm])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Must give a jack file path or a directory containing jack files as arg")
        sys.exit(1)

    Compiler(sys.argv[1]).main(sys.argv[2:])
