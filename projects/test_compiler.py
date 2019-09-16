#!/usr/bin/env python

from compiler import Compiler


class TestCompiler():
    compiler = Compiler()

    # Test end token with only primary type, no constraint on value (identifier)
    def test_match_token_varName(self):
        tokens = [{"type": "identifier",
                   "value": "myTest"}]
        tokens_type = "varName"

        excepted_out = {
            "is_match": True,
            "forward_index": len(tokens),
            "matched_tokens": tokens[0]
        }

        out = self.compiler.match_token(self.compiler.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test end token with an or on primary types, with constraint on value (symbol)
    def test_match_token_op(self):
        tokens = [{"type": "symbol",
                   "value": "&"}]
        tokens_type = "op"

        excepted_out = {
            "is_match": True,
            "forward_index": len(tokens),
            "matched_tokens": tokens[0]
        }

        out = self.compiler.match_token(self.compiler.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out

    # Test end token with an or on primary types, with constraint on value (keyword)
    def test_match_token_keywordConstant(self):
        tokens = [{"type": "keyword",
                   "value": "true"}]
        tokens_type = "keywordConstant"

        excepted_out = {
            "is_match": True,
            "forward_index": len(tokens),
            "matched_tokens": tokens[0]
        }

        out = self.compiler.match_token(self.compiler.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

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
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.compiler.match_token(self.compiler.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

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
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.compiler.match_token(self.compiler.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

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
            "forward_index": len(tokens),
            "matched_tokens": {
                "type": tokens_type,
                "value": tokens
            }
        }

        out = self.compiler.match_token(self.compiler.jack_syntax[tokens_type], tokens, current_object_name=tokens_type)

        assert out == excepted_out


    def test_sanitize_parsing_first_pass1(self):
        input_type = "class"
        input_values = [[
            {"type": "foo", "value": "Foo"},
            {"type": "bar", "value": "Bar"},
            {"type": "sub", "value": [
                [{"type": "sub1", "value": "Sub1"}, {"type": "sub2", "value": "Sub2"}],
                [{"type": "sub1", "value": "Sub1'"}, {"type": "sub2", "value": "Sub2'"}]
            ]},
        ]]
        excepted_output = [{
            "type": input_type,
            "value": [
                {"type": "foo", "value": "Foo"},
                {"type": "bar", "value": "Bar"},
                {"type": "sub", "value": [
                    {"type": "sub1", "value": "Sub1"},
                    {"type": "sub2", "value": "Sub2"}
                ]},
                {"type": "sub", "value": [
                    {"type": "sub1", "value": "Sub1'"},
                    {"type": "sub2", "value": "Sub2'"}
                ]}
            ]
        }]

        out = self.compiler.sanitize_parsing_first_pass(input_values, input_type)
        assert out == excepted_output

    def test_sanitize_parsing_first_pass2(self):
        input_type = "class"
        input_values = [
            [
                {'type': 'keyword', 'value': 'class'},
                {'type': 'identifier', 'value': 'Main'},
                {'type': 'symbol', 'value': '{'},
                {'type': 'classVarDec', 'value': [[
                    {'type': 'keyword', 'value': [[{'type': 'keyword', 'value': 'static'}]]},
                    {'type': 'type', 'value': [[
                        {'type': 'keyword', 'value': [[{'type': 'keyword', 'value': 'boolean'}]]}
                    ]]},
                    {'type': 'varName', 'value': [[{'type': 'identifier', 'value': 'test'}]]},
                    {'type': 'group', 'value': [[]]},
                    {'type': 'symbol', 'value': ';'}
                ], [[]]
                ]},
                {'type': 'subroutineDec',
                 'value': [
                     [{"type": "foo", "value": "bar1"}, {"type": "foo", "value": "bar2"}],
                     [{"type": "foo", "value": "bar1'"}, {"type": "foo", "value": "bar2'"}]
                 ]},
                {'type': 'symbol', 'value': '}'}
            ]
        ]

        excepted_output = [{
            "type": input_type,
            "value": [
                {'type': 'keyword', 'value': 'class'},
                {'type': 'identifier', 'value': 'Main'},
                {'type': 'symbol', 'value': '{'},
                {'type': 'classVarDec', 'value': [
                    {'type': 'keyword', 'value': [{'type': 'keyword', 'value': 'static'}]},
                    {'type': 'type', 'value': [
                        {'type': 'keyword', 'value': [{'type': 'keyword', 'value': 'boolean'}]}
                    ]},
                    {'type': 'varName', 'value': [{'type': 'identifier', 'value': 'test'}]},
                    {'type': 'symbol', 'value': ';'}
                ]},

                {'type': 'subroutineDec',
                 'value': [
                     {"type": "foo", "value": "bar1"},
                     {"type": "foo", "value": "bar2"},
                 ]},

                {'type': 'subroutineDec',
                 'value': [
                     {"type": "foo", "value": "bar1'"},
                     {"type": "foo", "value": "bar2'"}
                 ]},

                {'type': 'symbol', 'value': '}'}
            ]
        }]

        out = self.compiler.sanitize_parsing_first_pass(input_values, input_type)
        assert out == excepted_output
