import re
from xml.sax.saxutils import escape

class JackTokenizer:
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
        # Type: 'int' | 'char' | 'boolean' | className
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
                {"custom_type": "keywordConstant"},
                {"custom_type": "subroutineCall"},
                {"group": [
                    {"custom_type": "varName"},
                    {"type": "symbol", "value": "["},
                    {"custom_type": "expression"},
                    {"type": "symbol", "value": "]"},
                ]},
                {"group": [
                    {"type": "symbol", "value": "("},
                    {"custom_type": "expression"},
                    {"type": "symbol", "value": ")"},
                ]},
                {"group": [
                    {"custom_type": "unaryOp"},
                    {"custom_type": "term"},
                ]},
                {"custom_type": "varName"},
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
            self.tokens_xml.append( "<{}> {} </{}>".format(token["type"], escape(token["value"]), token["type"]))
        self.tokens_xml.append("</tokens>")

        # Parse raw token to build AST
        self.build_ast()

    def match_token(self, tokens_to_match, tokens, count=None, current_object_name=None):
        i = 0
        is_match = True
        matched_tokens = []

        for current_object in tokens_to_match:
            if len(tokens[i:]) == 0:
                if "count" not in current_object or current_object["count"] not in ["*", "?"]:
                    is_match = False
                break

            current_object_count = current_object["count"] if "count" in current_object else None

            # Primary type
            if "type" in current_object:
                if tokens[i]["type"] != current_object["type"]:
                    # Type mismatch
                    is_match = False
                    break
                if "value" in current_object and tokens[i]["value"] != current_object["value"]:
                    # Value mismatch
                    is_match = False
                    break

                matched_tokens.append(tokens[i])
                i += 1
                continue

            if "custom_type" in current_object:
                res = self.match_token(self.jack_syntax[current_object["custom_type"]], tokens[i:], current_object_count, current_object["custom_type"])
                if not res["is_match"]:
                    is_match = False
                    break

                if res["forward_index"] > 0 or current_object_count not in ("*", "?"):
                    if res["multiple_tokens"]:
                        for token in res["matched_tokens"]["value"]:
                            matched_tokens.append({
                                "type": res["matched_tokens"]["type"],
                                "value": token
                            })
                    else:
                        matched_tokens.append(res["matched_tokens"])
                i += res["forward_index"]
                continue

            if "or" in current_object:
                match_once = False
                for or_tokens in current_object["or"]:
                    res = self.match_token([or_tokens], tokens[i:], current_object_count, or_tokens["type"] if "type" in or_tokens else None)
                    if res["is_match"]:
                        match_once = True

                        if res["matched_tokens"]["type"] and res["forward_index"] > 0:
                            if res["multiple_tokens"]:
                                for token in res["matched_tokens"]["value"]:
                                    matched_tokens.append({
                                        "type": res["matched_tokens"]["type"],
                                        "value": token
                                    })
                            else:
                                matched_tokens.append(res["matched_tokens"])

                        else:
                            # TODO test
                            if res["multiple_tokens"]:
                                for token in res["matched_tokens"]["value"]:
                                    matched_tokens.append({
                                        "type": res["matched_tokens"]["type"],
                                        "value": token
                                    })
                            elif type(res["matched_tokens"]["value"]) == list:
                                matched_tokens += res["matched_tokens"]["value"]
                            else:
                                matched_tokens += res["matched_tokens"]

                        i += res["forward_index"]
                        break
                if not match_once:
                    is_match = False
                    break
                continue

            if "group" in current_object:
                res = self.match_token(current_object["group"], tokens[i:], current_object_count, None)
                if not res["is_match"]:
                    is_match = False
                    break

                if res["multiple_tokens"]:
                    for token in res["matched_tokens"]["value"]:
                        matched_tokens.append({
                            "type": res["matched_tokens"]["type"],
                            "value": token
                        })
                elif type(res["matched_tokens"]["value"]) == list:
                    matched_tokens += res["matched_tokens"]["value"]
                else:
                    matched_tokens.append(res["matched_tokens"])

                i += res["forward_index"]
                continue

        if not is_match:
            matched_tokens = []
            i = 0

        # Don't add these token in AST
        ignored_tokens = ["statement", "subroutineCall"]
        for token_idx, token in enumerate(matched_tokens):
            if token["type"] in ignored_tokens:
                if len(matched_tokens) == 1:
                    matched_tokens = matched_tokens[0]["value"]
                else:
                    matched_tokens[token_idx] = token["value"]
        matched_tokens = self.flatten(matched_tokens)

        forced_token = ["expression", "term"]
        if len(matched_tokens) == 1 and self.is_primitive_token_type(matched_tokens[0]["type"]) and current_object_name not in forced_token:
            current_object_name = matched_tokens[0]["type"]
            matched_tokens = matched_tokens[0]["value"]

        if count == "*":
            multiple_tokens = False
            if is_match:
                # See if we can match more of the pattern
                res = self.match_token(tokens_to_match, tokens[i:], count, current_object_name)

                if res['is_match'] and res["forward_index"] > 0 and current_object_name:
                    # We want to create several token of current type
                    matched_tokens = [matched_tokens]
                    multiple_tokens = True

                    if res["multiple_tokens"]:
                        matched_tokens += res["matched_tokens"]['value']
                    else:
                        matched_tokens.append(res["matched_tokens"]['value'])

                elif type(res["matched_tokens"]["value"]) == list:
                    matched_tokens += res["matched_tokens"]["value"]
                else:
                    matched_tokens += res["matched_tokens"]

                i += res["forward_index"]
            return {"is_match": True, "forward_index": i, "multiple_tokens": multiple_tokens,
                    "matched_tokens": {"type": current_object_name, "value":  matched_tokens}}

        elif count == "?":
            return {"is_match": True, "forward_index": i, "multiple_tokens": False,
                    "matched_tokens": {"type": current_object_name, "value":  matched_tokens}}

        return {"is_match": is_match, "forward_index": i, "multiple_tokens": False,
                "matched_tokens": {"type": current_object_name, "value":  matched_tokens}}

    @staticmethod
    def is_primitive_token_type(token_type):
        return token_type in ("keyword", "symbol", "integerConstant", "identifier", "stringConstant")

    def flatten(self, array):
        if not array:
            return array
        if isinstance(array[0], list):
            return self.flatten(array[0]) + self.flatten(array[1:])
        return array[:1] + self.flatten(array[1:])

    def ast2xml(self, local_ast, indent_level=0):
        indent_spaces = ""
        for _ in range(indent_level):
            indent_spaces += " "

        ast_type = local_ast["type"]
        ast_value = local_ast["value"]

        if type(ast_value) != list:
            self.parsed_xml.append("{}<{}> {} </{}>".format(indent_spaces, ast_type, escape(ast_value), ast_type))

        else:
            self.parsed_xml.append("{}<{}>".format(indent_spaces, ast_type))
            for token in ast_value:
                self.ast2xml(token, indent_level+2)
            self.parsed_xml.append("{}</{}>".format(indent_spaces, ast_type))

    def build_ast(self):
        # Parse class
        res = self.match_token(self.jack_syntax["class"], self.tokens, current_object_name="class")

        if not res["is_match"]:
            raise ValueError("The current file isn't valid")

        if res["forward_index"] != len(self.tokens):
            raise ValueError("Not all tokens were parsed")

        self.ast = res["matched_tokens"]

        self.ast2xml(self.ast)

