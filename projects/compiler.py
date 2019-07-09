#!/usr/bin/env python

import sys
import re
import os
from pprint import pprint
from xml.sax.saxutils import escape



class Compiler:
    filename = ""
    tokens = []
    tokens_xml = []

    ast = []
    parsed_xml = []

    keyword_list = [
        "class",
        "constructor",
        "function",
        "method",
        "field",
        "static",
        "var",
        "int",
        "char",
        "boolean",
        "void",
        "true",
        "false",
        "null",
        "this",
        "let",
        "do",
        "if",
        "else",
        "while",
        "return",
    ]

    symbol_list = [
        "{",
        "}",
        "(",
        ")",
        "[",
        "]",
        ".",
        ",",
        ";",
        "+",
        "-",
        "*",
        "/",
        "&",
        "|",
        "<",
        ">",
        "=",
        "~",
    ]

    jack_syntax = {
        # #######################
        # ## Program structure ##
        # #######################

        # class: 'class' className '{' classVarDec* subroutineDec* '}' 
        "class": [
            {"type": "keyword", "value": "class"},
            {"type": "identifier"},
            {"type": "symbol", "value": "{"},
            {"custom_type": "classVarDec", "count": "*"},
            {"custom_type": "subroutineDec", "count": "*"},
            {"type": "symbol", "value": "}"},
        ],
        # classVarDec: ('static' | 'field' ) type varName (',' varName)* ';' 
        "classVarDec": [
            {"or": [
                {"type": "keyword", "value": "static"},
                {"type": "keyword", "value": "field"},
            ]},
            {"custom_type": "type"},
            {"custom_type": "varName"},
            {"group": [
                {"type": "symbol", "value": ","},
                {"custom_type": "varName"},
            ], "count": "*"},
            {"type": "symbol", "value": ";"},
        ],
        # type: 'int' | 'char' | 'boolean' | className 
        "type": [
            {"or": [
                {"type": "keyword", "value": "int"},
                {"type": "keyword", "value": "char"},
                {"type": "keyword", "value": "boolean"},
                {"custom_type": "className"},
            ]},
        ],
        # subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) subroutineName
        #                '(' parameterList ')' subroutineBody
        "subroutineDec": [
            {"or": [
                {"type": "keyword", "value": "constructor"},
                {"type": "keyword", "value": "function"},
                {"type": "keyword", "value": "method"},
            ]},
            {"or": [
                {"type": "keyword", "value": "void"},
                {"custom_type": "type"},
            ]},
            {"custom_type": "subroutineName"},
            {"type": "symbol", "value": "("},
            {"custom_type": "parameterList"},
            {"type": "symbol", "value": ")"},
            {"custom_type": "subroutineBody"},
        ],
        # parameterList: ( (type varName) (',' type varName)*)?
        "parameterList": [
            {"group": [
                {"group": [
                    {"custom_type": "type"},
                    {"custom_type": "varName"},
                ]},
                {"group": [
                    {"type": "symbol", "value": ","},
                    {"custom_type": "type"},
                    {"custom_type": "varName"},
                ], "count": "*"}

            ], "count": "?"}
        ],
        # subroutineBody: '{' varDec* statements '}'
        "subroutineBody": [
            {"type": "symbol", "value": "{"},
            {"custom_type": "varDec", "count": "*"},
            {"custom_type": "statements"},
            {"type": "symbol", "value": "}"},
        ],
        # varDec: 'var' type varName (',' varName)* ';'
        "varDec": [
            {"type": "keyword", "value": "var"},
            {"custom_type": "type"},
            {"custom_type": "varName"},
            {"group": [
                {"type": "symbol", "value": ","},
                {"custom_type": "varName"},
            ], "count": "*"},
            {"type": "symbol", "value": ";"},
        ],
        # className: Identifier
        "className": [
            {"type": "identifier"},
        ],
        # subroutineName: Identifier
        "subroutineName": [
            {"type": "identifier"},
        ],
        # varName: Identifier
        "varName": [
            {"type": "identifier"},
        ],

        # ################
        # ## Statements ##
        # ################

        # statements: statement*
        "statements": [
            {"custom_type": "statement", "count": "*"},
        ],
        # statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        "statement": [
            {"or": [
                {"custom_type": "letStatement"},
                {"custom_type": "ifStatement"},
                {"custom_type": "whileStatement"},
                {"custom_type": "doStatement"},
                {"custom_type": "returnStatement"},

            ]},
        ],
        # letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        "letStatement": [
            {"type": "keyword", "value": "let"},
            {"custom_type": "varName"},
            {"group": [
                {"type": "symbol", "value": "["},
                {"custom_type": "expression"},
                {"type": "symbol", "value": "]"},
            ], "count": "?"},
            {"type": "symbol", "value": "="},
            {"custom_type": "expression"},
            {"type": "symbol", "value": ";"},
        ],
        # ifStatement: 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        "ifStatement": [
            {"type": "keyword", "value": "if"},
            {"type": "symbol", "value": "("},
            {"custom_type": "expression"},
            {"type": "symbol", "value": ")"},
            {"type": "symbol", "value": "{"},
            {"custom_type": "statements"},
            {"type": "symbol", "value": "}"},
            {"group": [
                {"type": "keyword", "value": "else"},
                {"type": "symbol", "value": "{"},
                {"custom_type": "statements"},
                {"type": "symbol", "value": "}"},
            ], "count": "?"},
        ],
        # whileStatement: 'while' '(' expression ')' '{' statements '}'
        "whileStatement": [
            {"type": "keyword", "value": "while"},
            {"type": "symbol", "value": "("},
            {"custom_type": "expression"},
            {"type": "symbol", "value": ")"},
            {"type": "symbol", "value": "{"},
            {"custom_type": "statements"},
            {"type": "symbol", "value": "}"},
        ],
        # doStatement: 'do' subroutineCall ';'
        "doStatement": [
            {"type": "keyword", "value": "do"},
            {"custom_type": "subroutineCall"},
            {"type": "symbol", "value": ";"},
        ],
        # returnStatement 'return' expression? ';'
        "returnStatement": [
            {"type": "keyword", "value": "return"},
            {"custom_type": "expression", "count": "?"},
            {"type": "symbol", "value": ";"},
        ],

        # #################
        # ## Expressions ##
        # #################

        # expression: term (op term)*
        "expression": [
            {"custom_type": "term"},
            {"group": [
                {"custom_type": "op"},
                {"custom_type": "term"},
            ], "count": "*"}
        ],
        # term: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression
        #       ']' | subroutineCall | '(' expression ')' | unaryOp term
        "term": [
            {"or": [
                {"type": "integerConstant"},
                {"type": "stringConstant"},
                {"type": "keywordConstant"},
                {"custom_type": "varName"},
                {"group": [
                    {"custom_type": "varName"},
                    {"type": "symbol", "value": "["},
                    {"custom_type": "expression"},
                    {"type": "symbol", "value": "]"},
                ]},
                {"custom_type": "subroutineCall"},
                {"group": [
                    {"type": "symbol", "value": "("},
                    {"custom_type": "expression"},
                    {"type": "symbol", "value": ")"},
                ]},
                {"group": [
                    {"custom_type": "unaryOp"},
                    {"custom_type": "term"},
                ]},
            ]},

        ],
        # subroutineCall: subroutineName '(' expressionList ')' | ( className | varName) '.' subroutineName '('
        #                 expressionList ')'
        "subroutineCall": [
            {"or": [
                {"group": [
                    {"custom_type": "subroutineName"},
                    {"type": "symbol", "value": "("},
                    {"custom_type": "expressionList"},
                    {"type": "symbol", "value": ")"},
                ]},
                {"group": [
                    {"or": [
                        {"custom_type": "className"},
                        {"custom_type": "varName"},
                    ]},
                    {"type": "symbol", "value": "."},
                    {"custom_type": "subroutineName"},
                    {"type": "symbol", "value": "("},
                    {"custom_type": "expressionList"},
                    {"type": "symbol", "value": ")"},
                ]},
            ]},

        ],
        # expressionList: (expression (',' expression)* )?
        "expressionList": [
            {"group": [
                {"custom_type": "expression"},
                {"group": [
                    {"type": "symbol", "value": ","},
                    {"custom_type": "expression"},
                ], "count": "*"}
            ], "count": "?"},
        ],
        # op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
        "op": [
            {"or": [
                {"type": "symbol", "value": "+"},
                {"type": "symbol", "value": "-"},
                {"type": "symbol", "value": "*"},
                {"type": "symbol", "value": "/"},
                {"type": "symbol", "value": "&"},
                {"type": "symbol", "value": "|"},
                {"type": "symbol", "value": "<"},
                {"type": "symbol", "value": ">"},
                {"type": "symbol", "value": "="},
            ]}
        ],
        # unaryOp: '-' | '~'
        "unaryOp": [
            {"or": [
                {"type": "symbol", "value": "-"},
                {"type": "symbol", "value": "~"},
            ]}
        ],
        # keywordConstant: 'true' | 'false' | 'null' | 'this'
        "keywordConstant": [
            {"or": [
                {"type": "keyword", "value": "true"},
                {"type": "keyword", "value": "false"},
                {"type": "keyword", "value": "null"},
                {"type": "keyword", "value": "this"},
            ]}
        ],
    }

    def get_token_type(self, word):
        pattern_number = "^[0-9]+$"
        pattern_identifier = "^[a-zA-Z_][a-zA-Z0-9_]*$"

        if word in self.keyword_list:
            return 'keyword'
        elif word in self.symbol_list:
            return 'symbol'
        elif re.match(pattern_number, word):
            return 'integerConstant'
        elif re.match(pattern_identifier, word):
            return 'identifier'
        return None

    def tokenize_word(self, word):
        if len(word) == 0:
            return []

        token_type = self.get_token_type(word)
        if token_type:
            token = {"type": token_type, "value": word}
            return [token]

        for i in range(len(word)):
            token_type = self.get_token_type(word[:-i])
            if token_type:
                res = self.tokenize_word(word[-i:])
                token = {"type": token_type, "value": word[:-i]}
                return [token] + res

    def tokenize_file(self, file):
        self.filename = file.split('/')[-1]

        with open(file, "r") as f:
            raw = f.readlines()

        content = []

        for line in raw:
            without_inline_comment = line.split("//", maxsplit=1)[0]
            clean_line = without_inline_comment.strip()
            if clean_line != "":
                content.append(clean_line)

        line = " ".join(content)
        words = line.split(" ")

        in_string = False
        in_comment = False
        for word in words:
            # Handle multi-lines comments
            if not in_string and (word == "/*" or word == "/**"):
                in_comment = True
            if in_comment:
                if word == '*/':
                    in_comment = False
                continue

            # Handle strings
            quote_position = word.find('"')

            if not in_string and quote_position != -1:
                self.tokens += self.tokenize_word(word[:quote_position])

                word = word[quote_position+1:]
                quote_position = word.find('"')
                in_string = True
                current_string = []

            if in_string:
                if quote_position != -1:
                    # Ignore trailing quote
                    current_string.append(word[:quote_position])
                    word = word[quote_position+1:]

                    in_string = False
                    token = {"type": "stringConstant", "value": " ".join(current_string)}
                    self.tokens.append(token)
                else:
                    current_string.append(word)
                    continue

            self.tokens += self.tokenize_word(word)

        # Prepare XML
        self.tokens_xml.append("<tokens>")
        for token in self.tokens:
            self.tokens_xml.append("<{}> {} </{}>".format(token["type"], escape(token["value"]), token["type"]))
        self.tokens_xml.append("</tokens>")

    def parse_file(self):
        for i in range(len(self.tokens)):
            token = self.tokens[i]

            if token["type"] == "keyword":
                if token["value"] == "class":
                    self.ast.append(token)

                    # class identifier
                    i += 1
                    token = self.tokens[i]
                    if token["type"] != "identifier":
                        print("Wrong token type after 'class', should be 'identifier' and got {}".format(token),
                              file=sys.stderr)
                        break
                    self.ast.append(token)

                    # open bracket



            if token["type"] == "symbol" and token["value"] in ("{", "[", "("):
                pass
            pass

    def compile_file(self, file):
        self.tokenize_file(file)
        self.parse_file()
        outfile_token = "{}T.xml".format(file.split(".jack", 1)[0])
        outfile_parsed = "{}.xml".format(file.split(".jack", 1)[0])

        with open(outfile_token, "w") as f:
            print("Write tokens result in {}".format(outfile_token))
            f.writelines(["{}\n".format(line) for line in self.tokens_xml])

        with open(outfile_token, "w") as f:
            print("Write parsed result in {}".format(outfile_parsed))
            # f.writelines(["{}\n".format(line) for line in self.parsed_xml])

    def main(self, file):
        if os.path.isdir(file):
            # Remove trailing slash
            if file.endswith("/"):
                file = file[:-1]

            for dir_file in os.listdir(file):
                abs_path = '{}/{}'.format(file, dir_file)
                if os.path.isfile(abs_path) and dir_file.endswith('.jack'):
                    print("Parse {}".format(abs_path))
                    self.compile_file(abs_path)
        else:
            self.compile_file(file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Must give a jack file path or a directory containing jack files as arg")
        sys.exit(1)

    Compiler().main(file=sys.argv[1])
