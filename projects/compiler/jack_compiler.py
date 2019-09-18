class JackCompiler:
    vm = []
    className = ""

    symbol_table_class = {}
    symbol_table_methods = {}

    def find_token(self, ast, name):
        return [token for token in ast["value"] if token["type"] == name]


    def compile_ast(self, ast, ast_type="class"):
        if ast_type == "class":
            self.className = ast["value"][1]["value"]

        for token in ast["value"]:
            if token["type"] == "subroutineDec":
                symbol_table_method = {}

                current_method = token["value"][2]["value"]
                current_method_type = token["value"][0]["value"]
                current_method_params = self.find_token(token, "parameterList")[0]["value"]

                self.symbol_table_methods[current_method] = {"type": current_method_type,
                                                             "return_type": token["value"][1]["value"],
                                                             "parameters": current_method_params}

                self.vm.append("function {}.{} {}".format(self.className, current_method, len(current_method_params)))
                if current_method_type in ["method", "constructor"]:
                    self.vm.append("push argument 0")
                    self.vm.append("pop pointer 0")

                subroutineBody = self.find_token(token, "subroutineBody")[0]
                statements = self.find_token(subroutineBody, "statements")[0]
                for statement in statements["value"]:
                    self.compile_statement(statement, symbol_table_method)
        pass

    def compile_statement(self, statement, symbol_table):
        if statement["type"] == "doStatement":
            is_current_class_method = False
            method_arg_count = 0
            args = []

            # Is it a method of another class with a dot
            if statement["value"][2]["type"] == "symbol" and statement["value"][2]["value"] == ".":
                method_name = "{}.{}".format(statement["value"][1]["value"], statement["value"][3]["value"])
                args = statement["value"][5]["value"]
            else:
                method_name = "{}".format(statement["value"][1]["value"])
                args = statement["value"][3]["value"]

                if method_name in self.symbol_table_methods:
                    is_current_class_method = True
                    method_name = "{}.{}".format(self.className, method_name)
                    method_arg_count += 1

            method_arg_count += len(args)
            if is_current_class_method:
                self.vm.append("push argument 0") # Push this

            for arg in args:
                self.compile_expression(arg["value"], symbol_table)

            self.vm.append("call {} {}".format(method_name, method_arg_count))

        if statement["type"] == "returnStatement":
            if len(statement["value"]) == 2:
                self.vm.append("push constant 0")
                self.vm.append("return")

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

            else:
                raise ValueError("Unknown term type {}".format(terms[0]["type"]))

        elif len(terms) == 3:
            self.compile_expression(terms[1]["value"], symbol_table)
        else:
            raise ValueError("Unknown term length {}".format(len(terms)))


    def compile_op(self, op):
        if op == "+":
            self.vm.append("add")
        elif op == "*":
            self.vm.append("call Math.multiply 2")
        else:
            raise ValueError("Unknown op {}".format(op))
