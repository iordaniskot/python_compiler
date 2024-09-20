

from ast_node import (
    AssignNode,
    IfNode,
    RepeatNode,
    ReadNode,
    WriteNode,
    BinaryOpNode,
    NumberNode,
    IdNode,
)


class CodeGenerator:
    def __init__(self):
        self.code = []
        self.symbol_table = {}
        self.var_count = 0
        self.next_memory_address = 1
        self.write_count = 0
        self.label_count = 0
        self.temp_count = 1
        self.temp_vars = set()
        self.temp_result = None

    def generate(self, ast):

        for statement in ast:
            self.generate_statement(statement)


        full_code = "\n".join(self.code)
        return full_code

    def generate_statement(self, node):
        if isinstance(node, AssignNode):
            self.generate_assign(node)
        elif isinstance(node, IfNode):
            self.generate_if(node)
        elif isinstance(node, RepeatNode):
            self.generate_repeat(node)
        elif isinstance(node, ReadNode):
            self.generate_read(node)
        elif isinstance(node, WriteNode):
            self.generate_write(node)
        else:
            raise NotImplementedError(f"Unknown statement node type: {type(node)}")

    def generate_assign(self, node):
        var_name = node.var
        var_addr = self.find_memory_location(var_name)

        self.generate_expression(node.value)

        self.code.append(f"         STA {var_addr}(0:5)")

    def generate_if(self, node):
        then_label = self.new_label('THEN')
        endif_label = self.new_label('ENDIF')
        else_label = self.new_label('ELSE') if node.else_branch else None

        self.generate_condition(node.condition)

        if node.condition.operator == 'LESS_THAN':
            self.code.append(f"         JL {then_label}")
        elif node.condition.operator == 'EQUALS':
            self.code.append(f"         JE {then_label}")
        else:
            raise NotImplementedError(f"Unknown operator in condition: {node.condition.operator}")

        if else_label:
            self.code.append(f"         JMP {else_label}")
        else:
            self.code.append(f"         JMP {endif_label}")

        self.code.append(f"{then_label:<8}NOP")
        for stmt in node.then_branch:
            self.generate_statement(stmt)

        if else_label:
            self.code.append(f"         JMP {endif_label}")
            self.code.append(f"{else_label:<8}NOP")
            for stmt in node.else_branch:
                self.generate_statement(stmt)

        self.code.append(f"{endif_label:<8}NOP")

    def generate_repeat(self, node):
        repeat_label = self.new_label('REPEAT')
        end_repeat_label = self.new_label('ENDREP')

        self.code.append(f"{repeat_label:<8}NOP")

        for stmt in node.body:
            self.generate_statement(stmt)

        self.generate_condition(node.condition)

        if node.condition.operator == 'EQUALS':
            self.code.append(f"         JE {end_repeat_label}")
        elif node.condition.operator == 'LESS_THAN':
            self.code.append(f"         JL {end_repeat_label}")
        else:
            raise NotImplementedError(f"Unknown operator in repeat condition: {node.condition.operator}")

        self.code.append(f"         JMP {repeat_label}")
        self.code.append(f"{end_repeat_label:<8}NOP")

    def generate_read(self, node):
        var_addr = self.find_memory_location(node.var)

        if var_addr is None:
            print("Error")
        else:
            inputBuffer = 1000
            inputDevice = 19
            self.code.append(f"         IN {inputBuffer}({inputDevice})")
            self.code.append(f"         JBUS *({inputDevice})")
            self.code.append(f"         LDX {inputBuffer}(0:5)")
            self.code.append(f"         NUM")
            self.code.append(f"         STA {var_addr}(0:5)")

    def generate_write(self, node):
        var_addr = self.find_memory_location(node.var)

        if var_addr is None:
            print("Error")
        else:
            self.write_count += 1
            self.code.append(f"         LDA {var_addr}(0:5)")
            self.code.append(f"         CHAR")
            self.code.append(f"         STA 1987(0:5)")
            self.code.append(f"         STX 1988(0:5)")
            self.code.append(f"         ENTX 45")
            self.code.append(f"         JAN KPO{self.write_count}")
            self.code.append(f"         ENTX 44")
            self.code.append(f"KPO{self.write_count:<6}NOP")
            self.code.append(f"         STX 1986(0:5)")
            self.code.append(f"         OUT 1986(2:3)")

    def generate_expression(self, node):
        if isinstance(node, NumberNode):
            self.generate_number(node)
        elif isinstance(node, IdNode):
            self.generate_id(node)
        elif isinstance(node, BinaryOpNode):
            self.generate_binary_op(node)
        else:
            raise NotImplementedError(f"Unknown expression node type: {type(node)}")

    def generate_number(self, node):
        self.code.append(f"         ENTA {node.value}")
        temp_var = self.allocate_temp()
        temp_addr = self.symbol_table[temp_var]
        self.code.append(f"         STA {temp_addr}(0:5)")
        self.temp_result = temp_addr

    def generate_id(self, node):
        var_addr = self.find_memory_location(node.name)
        self.code.append(f"         LDA {var_addr}(0:5)")
        temp_var = self.allocate_temp()
        temp_addr = self.symbol_table[temp_var]
        self.code.append(f"         STA {temp_addr}(0:5)")
        self.temp_result = temp_addr

    def generate_binary_op(self, node):
        operator = node.operator
        if operator == 'PLUS':
            self.generate_plus(node)
        elif operator == 'MINUS':
            self.generate_minus(node)
        elif operator == 'MULTIPLY':
            self.generate_mul(node)
        elif operator == 'DIVIDE':
            self.generate_div(node)
        elif operator == 'LESS_THAN':
            self.generate_lt(node)
        elif operator == 'EQUALS':
            self.generate_eq(node)
        else:
            raise NotImplementedError(f"Unknown binary operator: {operator}")

    def generate_plus(self, node):
        self.generate_expression(node.left)
        left_addr = self.temp_result
        temp_var_left = self.allocate_temp()
        temp_addr_left = self.symbol_table[temp_var_left]
        self.code.append(f"         STA {temp_addr_left}(0:5)")
        self.generate_expression(node.right)
        self.code.append(f"         ADD {temp_addr_left}(0:5)")
        temp_var_result = self.allocate_temp()
        temp_addr_result = self.symbol_table[temp_var_result]
        self.code.append(f"         STA {temp_addr_result}(0:5)")
        self.temp_result = temp_addr_result

    def generate_minus(self, node):
        self.generate_expression(node.left)
        left_addr = self.temp_result
        temp_var_left = self.allocate_temp()
        temp_addr_left = self.symbol_table[temp_var_left]
        self.code.append(f"         STA {temp_addr_left}(0:5)")
        self.generate_expression(node.right)
        self.code.append(f"         SUB {temp_addr_left}(0:5)")
        opptemp_addr = self.find_memory_location('OPPTEMP')
        self.code.append(f"         STA {opptemp_addr}(0:5)")
        self.code.append(f"         ENTA 0")
        self.code.append(f"         SUB {opptemp_addr}(0:5)")
        temp_var_result = self.allocate_temp()
        temp_addr_result = self.symbol_table[temp_var_result]
        self.code.append(f"         STA {temp_addr_result}(0:5)")
        self.temp_result = temp_addr_result

    def generate_mul(self, node):
        temp_var = self.allocate_temp()
        temp_addr = self.symbol_table[temp_var]
        self.code.append(f"         STZ {temp_addr}(0:5)")
        self.generate_expression(node.left)
        self.code.append(f"         STA {temp_addr}(0:5)")
        self.generate_expression(node.right)
        self.code.append(f"         MUL {temp_addr}(0:5)")
        self.code.append(f"         STX {temp_addr}(0:5)")
        self.code.append(f"         LDA {temp_addr}(0:5)")
        self.code.append(f"         ENTX 0")
        temp_var_result = self.allocate_temp()
        temp_addr_result = self.symbol_table[temp_var_result]
        self.code.append(f"         STA {temp_addr_result}(0:5)")
        self.temp_result = temp_addr_result

    def generate_div(self, node):
        if "SWAPTEMP" not in self.symbol_table:
            self.symbol_table["SWAPTEMP"] = self.next_memory_address
            self.next_memory_address += 1
        
        swaptmp_addr = self.symbol_table["SWAPTEMP"]

        temp_var = self.allocate_temp()
        temp_addr = self.symbol_table[temp_var]

        self.generate_expression(node.left)
        self.code.append(f"         STA {temp_addr}(0:5)")

        self.generate_expression(node.right)

        self.code.append(f"         STA {swaptmp_addr}(0:5)")
        self.code.append(f"         LDX {swaptmp_addr}(0:5)")
        self.code.append(f"         LDA {temp_addr}(0:5)")
        self.code.append(f"         STX {temp_addr}(0:5)")
        self.code.append(f"         LDA {swaptmp_addr}(0:5)")
        self.code.append(f"         LDX {temp_addr}(0:5)")

        self.code.append(f"         ENTA 0")
        self.code.append(f"         DIV {temp_addr}(0:5)")

        temp_var_result = self.allocate_temp()
        temp_addr_result = self.symbol_table[temp_var_result]
        self.code.append(f"         STA {temp_addr_result}(0:5)")
        self.temp_result = temp_addr_result

    def generate_lt(self, node):
        self.generate_expression(node.left)
        left_addr = self.temp_result
        self.generate_expression(node.right)
        right_addr = self.temp_result
        self.code.append(f"         LDA {left_addr}(0:5)")
        self.code.append(f"         CMPA {right_addr}(0:5)")

    def generate_eq(self, node):
        self.generate_expression(node.left)
        left_addr = self.temp_result
        self.generate_expression(node.right)
        right_addr = self.temp_result
        self.code.append(f"         LDA {left_addr}(0:5)")
        self.code.append(f"         CMPA {right_addr}(0:5)")

    def generate_condition(self, node):
        if isinstance(node, BinaryOpNode):
            if node.operator in ('LESS_THAN', 'EQUALS'):
                self.generate_binary_op(node)
            else:
                raise NotImplementedError(f"Unsupported operator in condition: {node.operator}")
        else:
            raise NotImplementedError(f"Unsupported condition node type: {type(node)}")

    def find_memory_location(self, symbol):
        symbol_upper = symbol.upper()
        if symbol_upper not in self.symbol_table:
            self.symbol_table[symbol_upper] = self.next_memory_address
            self.next_memory_address += 1
        return self.symbol_table[symbol_upper]

    def new_label(self, base='L'):
        label = f"{base}{self.label_count}"
        self.label_count += 1

    def allocate_temp(self):
        temp_var_name = f"TEMP{self.temp_count}"
        temp_addr = self.next_memory_address
        self.symbol_table[temp_var_name] = temp_addr
        self.next_memory_address += 1
        self.temp_count += 1
        return temp_var_name