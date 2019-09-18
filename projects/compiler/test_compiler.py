#!/usr/bin/env python

from compiler.jack_tokenizer import JackTokenizer

class TestJackTokenizer:
    tokenizer = JackTokenizer()

    # Test end token with only primary type, no constraint on value (identifier)
    def test_match_token_varName(self):
        tokens = [{"type": "identifier",
                   "value": "myTest"}]
        tokens_type = "varName"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": tokens[0]
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test end token with an or on primary types, with constraint on value (symbol)
    def test_match_token_op(self):
        tokens = [{"type": "symbol",
                   "value": "&"}]
        tokens_type = "op"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": tokens[0]
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test end token with an or on primary types, with constraint on value (keyword)
    def test_match_token_keywordConstant(self):
        tokens = [{"type": "keyword",
                   "value": "true"}]
        tokens_type = "keywordConstant"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": tokens[0]
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test matching multiple tokens + empty group
    def test_match_token_single_varDec(self):
        tokens = [
            {"type": "keyword", "value": "var"},
            {"type": "keyword", "value": "int"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": ";"}
        ]
        tokens_type = "varDec"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test matching multiple tokens + one member in group
    def test_match_token_double_varDec(self):
        tokens = [
            {"type": "keyword", "value": "var"},
            {"type": "keyword", "value": "int"},
            {"type": "identifier", "value": "myVar1"},
            {"type": "symbol", "value": ","},
            {"type": "identifier", "value": "myVar2"},
            {"type": "symbol", "value": ";"}
        ]
        tokens_type = "varDec"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test matching multiple tokens + two member in group
    def test_match_token_triple_varDec(self):
        tokens = [
            {"type": "keyword", "value": "var"},
            {"type": "keyword", "value": "int"},
            {"type": "identifier", "value": "myVar1"},
            {"type": "symbol", "value": ","},
            {"type": "identifier", "value": "myVar2"},
            {"type": "symbol", "value": ","},
            {"type": "identifier", "value": "myVar3"},
            {"type": "symbol", "value": ";"}
        ]
        tokens_type = "varDec"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_term_Integer(self):
        tokens = [
            {"type": "integerConstant", "value": "42"}
        ]
        tokens_type = "term"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": "term",
                "value":  [{
                    "type": "integerConstant",
                    "value": "42"
                }]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_term_NegInteger(self):
        tokens = [
            {"type": "symbol", "value": "-"},
            {"type": "integerConstant", "value": "42"}
        ]
        tokens_type = "term"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": "term",
                "value":  [
                    {"type": "symbol", "value": "-"},
                    {"type": "term", "value": [
                        {"type": "integerConstant", "value": "42"}
                    ]}
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_term_varNameArray(self):
        tokens = [
            {"type": "identifier", "value": "myArray"},
            {"type": "symbol", "value": "["},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "]"}
        ]
        tokens_type = "term"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "identifier", "value": "myArray"},
                    {"type": "symbol", "value": "["},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "integerConstant", "value": "42"},
                        ]},
                    ]},
                    {"type": "symbol", "value": "]"}
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_term_sum(self):
        tokens = [
            {"type": "symbol", "value": "("},
            {"type": "integerConstant", "value": "12"},
            {"type": "symbol", "value": "+"},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": ")"},
        ]
        tokens_type = "term"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "symbol", "value": "("},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "integerConstant", "value": "12"},
                        ]},
                        {"type": "symbol", "value": "+"},
                        {"type": "term", "value": [
                            {"type": "integerConstant", "value": "42"},
                        ]},
                    ]},
                    {"type": "symbol", "value": ")"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_expression_three_terms(self):
        tokens = [
            {"type": "integerConstant", "value": "12"},
            {"type": "symbol", "value": "+"},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "/"},
            {"type": "identifier", "value": "divider"},
        ]
        tokens_type = "expression"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "term", "value": [
                        {"type": "integerConstant", "value": "12"},
                    ]},
                    {"type": "symbol", "value": "+"},
                    {"type": "term", "value": [
                                {"type": "integerConstant", "value": "42"},
                    ]},
                    {"type": "symbol", "value": "/"},
                    {"type": "term", "value": [
                        {"type": "identifier", "value": "divider"},
                    ]},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_expression_three_complex_terms(self):
        tokens = [
            {"type": "symbol", "value": "-"},
            {"type": "integerConstant", "value": "12"},
            {"type": "symbol", "value": "+"},

            {"type": "identifier", "value": "myArray"},
            {"type": "symbol", "value": "["},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "]"},

            {"type": "symbol", "value": "/"},
            {"type": "identifier", "value": "divider"},
        ]
        tokens_type = "expression"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "term", "value": [
                        {"type": "symbol", "value": "-"},
                        {"type": "term", "value": [
                            {"type": "integerConstant", "value": "12"},
                        ]},
                    ]},
                    {"type": "symbol", "value": "+"},
                    {"type": "term", "value": [
                        {"type": "identifier", "value": "myArray"},
                        {"type": "symbol", "value": "["},
                        {"type": "expression", "value": [
                            {"type": "term", "value": [
                                {"type": "integerConstant", "value": "42"},
                            ]},
                        ]},
                        {"type": "symbol", "value": "]"},
                    ]},
                    {"type": "symbol", "value": "/"},
                    {"type": "term", "value": [
                        {"type": "identifier", "value": "divider"},
                    ]},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_expression_list(self):
        tokens = [
            {"type": "symbol", "value": "-"},
            {"type": "integerConstant", "value": "12"},
            {"type": "symbol", "value": "+"},
            {"type": "identifier", "value": "myArray"},
            {"type": "symbol", "value": "["},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "]"},
            {"type": "symbol", "value": "/"},
            {"type": "identifier", "value": "divider"},

            {"type": "symbol", "value": ","},

            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": "="},
            {"type": "integerConstant", "value": "1"},
        ]
        tokens_type = "expressionList"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "symbol", "value": "-"},
                            {"type": "term", "value": [
                                {"type": "integerConstant", "value": "12"},
                            ]},
                        ]},
                        {"type": "symbol", "value": "+"},
                        {"type": "term", "value": [
                            {"type": "identifier", "value": "myArray"},
                            {"type": "symbol", "value": "["},
                            {"type": "expression", "value": [
                                {"type": "term", "value": [
                                    {"type": "integerConstant", "value": "42"},
                                ]},
                            ]},
                            {"type": "symbol", "value": "]"},
                        ]},
                        {"type": "symbol", "value": "/"},
                        {"type": "term", "value": [
                            {"type": "identifier", "value": "divider"},
                        ]},
                    ]},
                    {"type": "symbol", "value": ","},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "identifier", "value": "myVar"},
                        ]},
                        {"type": "symbol", "value": "="},
                        {"type": "term", "value": [
                            {"type": "integerConstant", "value": "1"},
                        ]}
                    ]}
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_subroutineCall_function_no_arg(self):
        tokens = [
            {"type": "identifier", "value": "myFunc"},
            {"type": "symbol", "value": "("},
            {"type": "symbol", "value": ")"},
        ]
        tokens_type = "subroutineCall"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "identifier", "value": "myFunc"},
                    {"type": "symbol", "value": "("},
                    {"type": "expressionList", "value": []},
                    {"type": "symbol", "value": ")"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_subroutineCall_method_no_arg(self):
        tokens = [
            {"type": "identifier", "value": "myClass"},
            {"type": "symbol", "value": "."},
            {"type": "identifier", "value": "myMethod"},
            {"type": "symbol", "value": "("},
            {"type": "symbol", "value": ")"},
        ]
        tokens_type = "subroutineCall"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "identifier", "value": "myClass"},
                    {"type": "symbol", "value": "."},
                    {"type": "identifier", "value": "myMethod"},
                    {"type": "symbol", "value": "("},
                    {"type": "expressionList", "value": []},
                    {"type": "symbol", "value": ")"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_subroutineCall_function_one_arg(self):
        tokens = [
            {"type": "identifier", "value": "myFunc"},
            {"type": "symbol", "value": "("},
            {"type": "identifier", "value": "myArr"},
            {"type": "symbol", "value": "["},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "]"},
            {"type": "symbol", "value": ")"},
        ]
        tokens_type = "subroutineCall"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "identifier", "value": "myFunc"},
                    {"type": "symbol", "value": "("},
                    {"type": "expressionList", "value": [
                        {"type": "expression", "value": [
                            {"type": "term", "value": [
                                {"type": "identifier", "value": "myArr"},
                                {"type": "symbol", "value": "["},
                                {"type": "expression", "value": [
                                    {"type": "term", "value": [
                                        {"type": "integerConstant", "value": "42"},
                                    ]},
                                ]},
                                {"type": "symbol", "value": "]"},
                            ]},
                        ]},
                    ]},
                    {"type": "symbol", "value": ")"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_subroutineCall_function_three_args(self):
        tokens = [
            {"type": "identifier", "value": "myFunc"},
            {"type": "symbol", "value": "("},
            {"type": "identifier", "value": "myArr"},
            {"type": "symbol", "value": "["},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "]"},
            {"type": "symbol", "value": ","},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": ","},
            {"type": "symbol", "value": "-"},
            {"type": "identifier", "value": "myVar2"},
            {"type": "symbol", "value": ")"},
        ]
        tokens_type = "subroutineCall"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "identifier", "value": "myFunc"},
                    {"type": "symbol", "value": "("},
                    {"type": "expressionList", "value": [
                        {"type": "expression", "value": [
                            {"type": "term", "value": [
                                {"type": "identifier", "value": "myArr"},
                                {"type": "symbol", "value": "["},
                                {"type": "expression", "value": [
                                    {"type": "term", "value": [
                                        {"type": "integerConstant", "value": "42"},
                                    ]},
                                ]},
                                {"type": "symbol", "value": "]"},
                            ]},
                        ]},
                        {"type": "symbol", "value": ","},
                        {"type": "expression", "value": [
                            {"type": "term", "value": [
                                {"type": "identifier", "value": "myVar"},
                            ]},
                        ]},
                        {"type": "symbol", "value": ","},
                        {"type": "expression", "value": [
                            {"type": "term", "value": [
                                {"type": "symbol", "value": "-"},
                                {"type": "term", "value": [
                                    {"type": "identifier", "value": "myVar2"},
                                ]},
                            ]},
                        ]},
                    ]},
                    {"type": "symbol", "value": ")"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_letStatement(self):
        tokens = [
            {"type": "keyword", "value": "let"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": "="},

            {"type": "identifier", "value": "myArr"},
            {"type": "symbol", "value": "["},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": "]"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "letStatement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "keyword", "value": "let"},
                    {"type": "identifier", "value": "myVar"},
                    {"type": "symbol", "value": "="},

                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "identifier", "value": "myArr"},
                            {"type": "symbol", "value": "["},
                            {"type": "expression", "value": [
                                {"type": "term", "value": [
                                    {"type": "integerConstant", "value": "42"},
                                ]},
                            ]},
                            {"type": "symbol", "value": "]"},
                        ]},
                    ]},
                    {"type": "symbol", "value": ";"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_letStatement_array(self):
        tokens = [
            {"type": "keyword", "value": "let"},
            {"type": "identifier", "value": "myArr"},
            {"type": "symbol", "value": "["},
            {"type": "identifier", "value": "idx"},
            {"type": "symbol", "value": "]"},
            {"type": "symbol", "value": "="},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "letStatement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "keyword", "value": "let"},
                    {"type": "identifier", "value": "myArr"},
                    {"type": "symbol", "value": "["},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "identifier", "value": "idx"},
                        ]},
                    ]},
                    {"type": "symbol", "value": "]"},
                    {"type": "symbol", "value": "="},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "integerConstant", "value": "42"},
                        ]},
                    ]},
                    {"type": "symbol", "value": ";"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_ifStatement(self):
        tokens = [
            {"type": "keyword", "value": "if"},
            {"type": "symbol", "value": "("},
            {"type": "keyword", "value": "true"},
            {"type": "symbol", "value": ")"},
            {"type": "symbol", "value": "{"},

            {"type": "keyword", "value": "let"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": "="},
            {"type": "integerConstant", "value": "42"},
            {"type": "symbol", "value": ";"},

            {"type": "symbol", "value": "}"},
        ]
        tokens_type = "ifStatement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "keyword", "value": "if"},
                    {"type": "symbol", "value": "("},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "keyword", "value": "true"},
                        ]},
                    ]},
                    {"type": "symbol", "value": ")"},
                    {"type": "symbol", "value": "{"},

                    {"type": "statements", "value": [
                        {"type": "letStatement", "value": [
                            {"type": "keyword", "value": "let"},
                            {"type": "identifier", "value": "myVar"},
                            {"type": "symbol", "value": "="},
                            {"type": "expression", "value": [
                                {"type": "term", "value": [
                                    {"type": "integerConstant", "value": "42"},
                                ]},
                            ]},
                            {"type": "symbol", "value": ";"},
                        ]},
                    ]},
                    {"type": "symbol", "value": "}"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_doStatement(self):
        tokens = [
            {"type": "keyword", "value": "do"},
            {"type": "identifier", "value": "myFunc"},
            {"type": "symbol", "value": "("},
            {"type": "symbol", "value": ")"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "doStatement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "keyword", "value": "do"},
                    {"type": "identifier", "value": "myFunc"},
                    {"type": "symbol", "value": "("},
                    {"type": "expressionList", "value": []},
                    {"type": "symbol", "value": ")"},
                    {"type": "symbol", "value": ";"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_returnStatement(self):
        tokens = [
            {"type": "keyword", "value": "return"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "returnStatement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "keyword", "value": "return"},
                    {"type": "expression", "value": [
                        {"type": "term", "value": [
                            {"type": "identifier", "value": "myVar"},
                        ]},
                    ]},
                    {"type": "symbol", "value": ";"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_returnStatement_no_return(self):
        tokens = [
            {"type": "keyword", "value": "return"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "returnStatement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "keyword", "value": "return"},
                    {"type": "symbol", "value": ";"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_statement(self):
        tokens = [
            {"type": "keyword", "value": "do"},
            {"type": "identifier", "value": "myFunc"},
            {"type": "symbol", "value": "("},
            {"type": "symbol", "value": ")"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "statement"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "doStatement", "value": [
                        {"type": "keyword", "value": "do"},
                        {"type": "identifier", "value": "myFunc"},
                        {"type": "symbol", "value": "("},
                        {"type": "expressionList", "value": []},
                        {"type": "symbol", "value": ")"},
                        {"type": "symbol", "value": ";"},
                    ]},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_statements_single_statement(self):
        tokens = [
            {"type": "keyword", "value": "do"},
            {"type": "identifier", "value": "myFunc"},
            {"type": "symbol", "value": "("},
            {"type": "symbol", "value": ")"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "statements"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "doStatement", "value": [
                        {"type": "keyword", "value": "do"},
                        {"type": "identifier", "value": "myFunc"},
                        {"type": "symbol", "value": "("},
                        {"type": "expressionList", "value": []},
                        {"type": "symbol", "value": ")"},
                        {"type": "symbol", "value": ";"},
                    ]},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_varDec(self):
        tokens = [
            {"type": "keyword", "value": "var"},
            {"type": "identifier", "value": "myClass"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "varDec"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_varDec_double(self):
        tokens = [
            {"type": "keyword", "value": "var"},
            {"type": "identifier", "value": "myClass"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": ","},
            {"type": "identifier", "value": "myVar2"},
            {"type": "symbol", "value": ";"},
        ]
        tokens_type = "varDec"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_subroutineBody(self):
        tokens = [
            {"type": "symbol", "value": "{"},
            {"type": "keyword", "value": "var"},
            {"type": "identifier", "value": "myClass"},
            {"type": "identifier", "value": "myVar"},
            {"type": "symbol", "value": ";"},

            {"type": "keyword", "value": "var"},
            {"type": "identifier", "value": "int"},
            {"type": "identifier", "value": "myVar2"},
            {"type": "symbol", "value": ";"},

            {"type": "keyword", "value": "return"},
            {"type": "symbol", "value": ";"},

            {"type": "symbol", "value": "}"},
        ]
        tokens_type = "subroutineBody"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "symbol", "value": "{"},
                    {"type": "varDec", "value": [
                        {"type": "keyword", "value": "var"},
                        {"type": "identifier", "value": "myClass"},
                        {"type": "identifier", "value": "myVar"},
                        {"type": "symbol", "value": ";"},
                    ]},

                    {"type": "varDec", "value": [
                        {"type": "keyword", "value": "var"},
                        {"type": "identifier", "value": "int"},
                        {"type": "identifier", "value": "myVar2"},
                        {"type": "symbol", "value": ";"},
                    ]},

                    {"type": "statements", "value": [
                        {"type": "returnStatement", "value": [
                            {"type": "keyword", "value": "return"},
                            {"type": "symbol", "value": ";"},
                        ]},
                    ]},

                    {"type": "symbol", "value": "}"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    def test_match_token_subroutineBody_triple_varDec(self):
        tokens = [
            {"type": "symbol", "value": "{"},
            {"type": "keyword", "value": "var"},
            {"type": "keyword", "value": "int"},
            {"type": "identifier", "value": "i"},
            {"type": "symbol", "value": ","},
            {"type": "identifier", "value": "j"},
            {"type": "symbol", "value": ";"},

            {"type": "keyword", "value": "var"},
            {"type": "identifier", "value": "String"},
            {"type": "identifier", "value": "s"},
            {"type": "symbol", "value": ";"},

            {"type": "keyword", "value": "var"},
            {"type": "identifier", "value": "Array"},
            {"type": "identifier", "value": "a"},
            {"type": "symbol", "value": ";"},

            {"type": "keyword", "value": "return"},
            {"type": "symbol", "value": ";"},

            {"type": "symbol", "value": "}"},
        ]
        tokens_type = "subroutineBody"

        excepted_out = {
            "is_match": True,
            "multiple_tokens": False,
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": [
                    {"type": "symbol", "value": "{"},
                    {"type": "varDec", "value": [
                        {"type": "keyword", "value": "var"},
                        {"type": "keyword", "value": "int"},
                        {"type": "identifier", "value": "i"},
                        {"type": "symbol", "value": ","},
                        {"type": "identifier", "value": "j"},
                        {"type": "symbol", "value": ";"},
                    ]},

                    {"type": "varDec", "value": [
                        {"type": "keyword", "value": "var"},
                        {"type": "identifier", "value": "String"},
                        {"type": "identifier", "value": "s"},
                        {"type": "symbol", "value": ";"},
                    ]},

                    {"type": "varDec", "value": [
                        {"type": "keyword", "value": "var"},
                        {"type": "identifier", "value": "Array"},
                        {"type": "identifier", "value": "a"},
                        {"type": "symbol", "value": ";"},
                    ]},

                    {"type": "statements", "value": [
                        {"type": "returnStatement", "value": [
                            {"type": "keyword", "value": "return"},
                            {"type": "symbol", "value": ";"},
                        ]},
                    ]},

                    {"type": "symbol", "value": "}"},
                ]
            }
        }

        out = self.tokenizer.match_token(self.tokenizer.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out
