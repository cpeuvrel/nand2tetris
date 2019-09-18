#!/usr/bin/env python

import sys
import os

from compiler.jack_tokenizer import JackTokenizer

class Compiler:
    filename = ""
    def __init__(self, filename):
        self.filename = filename

    def main(self):
        if os.path.isdir(self.filename):
            # Remove trailing slash
            if self.filename.endswith("/"):
                self.filename = self.filename[:-1]

            for dir_file in os.listdir(self.filename):
                abs_path = '{}/{}'.format(self.filename, dir_file)
                if os.path.isfile(abs_path) and dir_file.endswith('.jack'):
                    print("Parse {}".format(abs_path))
                    self.compile_file(abs_path)
        else:
            self.compile_file(self.filename)

    @staticmethod
    def compile_file(file):
        tokenizer = JackTokenizer()

        tokenizer.tokenize_file(file)

        outfile_token = "{}T.xml".format(file.split(".jack", 1)[0])
        outfile_parsed = "{}.xml".format(file.split(".jack", 1)[0])

        with open(outfile_token, "w") as f:
            print("Write tokens result in {}".format(outfile_token))
            f.writelines(["{}\n".format(line) for line in tokenizer.tokens_xml])

        with open(outfile_parsed, "w") as f:
            print("Write parsed result in {}".format(outfile_parsed))
            f.writelines(["{}\n".format(line) for line in tokenizer.parsed_xml])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Must give a jack file path or a directory containing jack files as arg")
        sys.exit(1)

    Compiler(sys.argv[1]).main()
