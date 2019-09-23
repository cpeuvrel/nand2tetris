class JackCompiler:
    vm = []
    className = ""

    symbol_table_class = {}
    symbol_table_methods = {}

    while_label_counter = 0
    if_label_counter = 0

    def find_token(self, ast, name):
        return [token for token in ast["value"] if token["type"] == name]

    def compile_ast(self, ast, ast_type="class"):
        if ast_type == "class":
            self.className = ast["value"][1]["value"]

        # Quick first pass to fill symbol_table_methods
        for subroutine in self.find_token(ast, "subroutineDec"):
            current_method = subroutine["value"][2]["value"]
            current_method_type = subroutine["value"][0]["value"]
            current_method_params = self.find_token(subroutine, "parameterList")[0]["value"]

            self.symbol_table_methods[current_method] = {"type": current_method_type,
                                                         "return_type": subroutine["value"][1]["value"],
                                                         "parameters": current_method_params}

        for token in ast["value"]:
            if token["type"] == "classVarDec":
                self.record_var({"type": token["value"][1]["value"],
                                 "value": [value for i, value in enumerate(token["value"]) if i > 0]},
                                "this",
                                self.symbol_table_class,
                                common_type=True)

            elif token["type"] == "subroutineDec":
                symbol_table_method = {}

                current_method_name = token["value"][2]["value"]
                current_method = self.symbol_table_methods[current_method_name]

                parameter_list = self.find_token(token, "parameterList")[0]
                subroutine_body = self.find_token(token, "subroutineBody")[0]
                var_decs = self.find_token(subroutine_body, "varDec")

                local_args_count = 0
                for var_dec in var_decs:
                    local_args_count += int((len(var_dec["value"])-2) / 2)

                self.vm.append("function {}.{} {}".format(self.className, current_method_name, local_args_count))
                if current_method["type"] == "method":
                    self.vm.append("push argument 0")
                    self.vm.append("pop pointer 0")

                self.record_var(parameter_list, "argument", symbol_table_method)

                for var in var_decs:
                    self.record_var({"type": var["type"],
                                     "value": [value for i, value in enumerate(var["value"]) if i > 0]},
                                    "local",
                                    symbol_table_method,
                                    common_type=True)

                statements = self.find_token(subroutine_body, "statements")[0]
                for statement in statements["value"]:
                    self.compile_statement(statement, symbol_table_method)
        pass

    def record_var(self, declaration, segment, symbol_table, common_type=False):
        next_var_pos = 0
        i = 0
        var_name_offset = 1
        if len(declaration["value"]) < 2:
            return

        if common_type:
            var_type = declaration["value"][0]["value"]
            var_name_offset = 0
            i += 1

        for _ in [var for var in symbol_table if symbol_table[var]["segment"] == segment]:
            next_var_pos += 1

        while len(declaration["value"]) > i and declaration["value"][i+var_name_offset]["type"] == "identifier":
            if not common_type:
                var_type = declaration["value"][i]["value"]
                var_name = declaration["value"][i+1]["value"]
                i += 1
            else:
                var_name = declaration["value"][i]["value"]

            symbol_table[var_name] = {"type": var_type,
                                      "segment": segment,
                                      "pos": next_var_pos}
            next_var_pos += 1
            i += 2

    def compile_statement(self, statement, symbol_table):
        if statement["type"] == "letStatement":
            varname = statement["value"][1]["value"]
            is_array = False

            if varname not in symbol_table and varname not in self.symbol_table_class:
                raise KeyError("Unkwnown variable '{}'".format(varname))
            var = symbol_table[varname] if varname in symbol_table else self.symbol_table_class[varname]

            if statement["value"][2]["value"] == "[":
                segment = "pointer"
                pos = 1
                is_array = True

                self.compile_expression(statement["value"][3]["value"], symbol_table)
                self.vm.append("push {} {}".format(var["segment"], var["pos"]))
                self.vm.append("add")
            else:
                segment = var["segment"]
                pos = var["pos"]


            self.compile_expression(statement["value"][-2]["value"], symbol_table)

            self.vm.append("pop {} {}".format(segment, pos))
            if is_array:
                self.vm.append("push temp 0")
                self.vm.append("pop that 0")

        elif statement["type"] == "ifStatement":
            label_true = "IF_TRUE{}".format(self.if_label_counter)
            label_false = "IF_FALSE{}".format(self.if_label_counter)
            label_end = "IF_END{}".format(self.if_label_counter)
            self.if_label_counter += 1

            is_else = len(statement["value"]) == 11

            #   code for computing cond
            self.compile_expression(statement["value"][2]["value"], symbol_table)

            #   if-goto true
            self.vm.append("if-goto {}".format(label_true))
            self.vm.append("goto {}".format(label_false))

            self.vm.append("label {}".format(label_true))
            #   code for executing s1
            for sub_statement in statement["value"][5]["value"]:
                self.compile_statement(sub_statement, symbol_table)
            #   goto L2
            self.vm.append("goto {}".format(label_end))

            # label L1
            self.vm.append("label {}".format(label_false))

            if is_else:
                #   code for executing s2
                for sub_statement in statement["value"][9]["value"]:
                    self.compile_statement(sub_statement, symbol_table)

            # label L2
            self.vm.append("label {}".format(label_end))



        elif statement["type"] == "whileStatement":
            label_begin = "WHILE_EXP{}".format(self.while_label_counter)
            label_end = "WHILE_END{}".format(self.while_label_counter)
            self.while_label_counter += 1

            # label L1
            self.vm.append("label {}".format(label_begin))

            #   code for computing ~cond
            self.compile_expression(statement["value"][2]["value"], symbol_table)
            self.compile_op("~", unary_op=True)

            #   if-goto L2
            self.vm.append("if-goto {}".format(label_end))

            #   code for executing s1
            for sub_statement in statement["value"][5]["value"]:
                self.compile_statement(sub_statement, symbol_table)

            #   goto L1
            self.vm.append("goto {}".format(label_begin))

            # label L2
            self.vm.append("label {}".format(label_end))

        elif statement["type"] == "doStatement":
            self.compile_subroutine_call(statement["value"][1]["value"], symbol_table)

        elif statement["type"] == "returnStatement":
            if len(statement["value"]) == 2:
                self.vm.append("push constant 0")
                self.vm.append("return")
            elif len(statement["value"]) == 3:
                self.compile_expression(statement["value"][1]["value"], symbol_table)
                self.vm.append("return")
        else:
            raise ValueError("Unknown statement {}".format(statement["type"]))

    def compile_subroutine_call(self, tokens, symbol_table):
        is_current_class_method = False
        method_arg_count = 0
        args = []

        # Is it a method of another class with a dot
        if tokens[1]["type"] == "symbol" and tokens[1]["value"] == ".":
            method_name = "{}.{}".format(tokens[0]["value"], tokens[2]["value"])
            args = tokens[4]["value"]
        else:
            method_name = "{}".format(tokens[0]["value"])
            args = tokens[2]["value"]

            if method_name in self.symbol_table_methods:
                is_current_class_method = True
                method_name = "{}.{}".format(self.className, method_name)
                method_arg_count += 1

        # Skip odd args which are separating commas
        args = [arg for i, arg in enumerate(args) if i % 2 == 0]
        method_arg_count += len(args)
        if is_current_class_method:
            self.vm.append("push argument 0") # Push this

        for arg in args:
            self.compile_expression(arg["value"], symbol_table)

        self.vm.append("call {} {}".format(method_name, method_arg_count))

        # If function is known to return void or we don't know, pop its fake return value from the stack
        if method_name in self.symbol_table_methods and \
                self.symbol_table_methods[method_name]["return_type"] == "void" \
                or method_name not in self.symbol_table_methods:
            self.vm.append("pop temp 0")

    def compile_expression(self, expression, symbol_table):
        # compile expression[0]
        self.compile_term(expression[0]["value"], symbol_table)

        i=1
        while i < len(expression):
            self.compile_term(expression[i+1]["value"], symbol_table)
            self.compile_op(expression[i]["value"])

            i += 2

    def compile_term(self, terms, symbol_table):
        if len(terms) == 1:
            if terms[0]["type"] == "integerConstant":
                self.vm.append("push constant {}".format(terms[0]["value"]))
            elif terms[0]["type"] == "keyword":
                if terms[0]["value"] in ["null", "false"]:
                    self.vm.append("push constant 0")
                elif terms[0]["value"] == "true":
                    self.vm.append("push constant 0")
                    self.vm.append("not")
                else:
                    NotImplementedError("Not implemented keyword {}".format(terms[0]["value"]))
            elif terms[0]["type"] == "identifier":
                # Lookup variable
                identifier = terms[0]["value"]
                if identifier in symbol_table:
                    var = symbol_table[identifier]
                elif identifier in self.symbol_table_class:
                    var = self.symbol_table_class[identifier]
                else:
                    raise ValueError("Unknown identifier {}".format(identifier))
                self.vm.append("push {} {}".format(var["segment"], var["pos"]))

            elif terms[0]["type"] == "subroutineCall":
                # subroutineCall (with class.method)
                self.compile_subroutine_call(terms[0]["value"], symbol_table)

            elif terms[0]["type"] == "stringConstant":
                self.vm.append("push constant {}".format(len(terms[0]["value"])))
                self.vm.append("call String.new 1")
                for c in terms[0]["value"]:
                    self.vm.append("push constant {}".format(ord(c)))
                    self.vm.append("call String.appendChar 2")

            else:
                raise ValueError("Unknown term type {}".format(terms[0]["type"]))

        elif len(terms) == 2:
            # unaryOp term
            self.compile_term(terms[1]["value"], symbol_table)
            self.compile_op(terms[0]["value"], unary_op=True)
        elif len(terms) == 3:
            # '(' expression ')'
            self.compile_expression(terms[1]["value"], symbol_table)
        elif len(terms) == 4:
            #  identifier '[' expression ']'
            varname = terms[0]["value"]
            if varname not in symbol_table and varname not in self.symbol_table_class:
                raise KeyError("Unkwnown variable '{}'".format(varname))
            var = symbol_table[varname] if varname in symbol_table else self.symbol_table_class[varname]

            self.compile_expression(terms[2]["value"], symbol_table)

            self.vm.append("push {} {}".format(var["segment"], var["pos"]))
            self.vm.append("add")
            self.vm.append("pop pointer 1")
            self.vm.append("push that 0")

        else:
            raise ValueError("Unknown term length {}".format(len(terms)))


    def compile_op(self, op, unary_op=False):
        if op == "+":
            self.vm.append("add")
        elif op == "*":
            self.vm.append("call Math.multiply 2")
        elif op == "/":
            self.vm.append("call Math.divide 2")
        elif op == "-":
            if unary_op:
                self.vm.append("neg")
            else:
                self.vm.append("sub")
        elif op == "~":
            self.vm.append("not")
        elif op == "<":
            self.vm.append("lt")
        elif op == ">":
            self.vm.append("gt")
        elif op == "=":
            self.vm.append("eq")
        elif op == "&":
            self.vm.append("and")
        elif op == "|":
            self.vm.append("or")
        else:
            raise ValueError("Unknown op {}".format(op))
