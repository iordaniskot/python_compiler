# code_generator.py
from ast_node import *


class CodeGenerator:
    def __init__(self):
        self.label_counter = 0
        self.variables = set()

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self, ast):
        self.variables = self.find_variables(ast)

        mixal_code = "*Simple Language Compiler Output (MIXAL)\n* Assumptions:\n*   - Variables are stored in memory starting at address 1\n*   - Input and output are handled via MIX devices\n"

        # Variable Declarations: Reserve space for each variable
        for i, var in enumerate(self.variables):
            mixal_code += f"{var.upper():<10}CON     0        * Variable declaration"  # Uppercase and left-align

        mixal_code += """
        ENT1    0
        JMP     START
        """
        for statement in ast:
            mixal_code += self.generate_statement(statement)
        mixal_code += "START   OUT     MSG(ENDMSG)\n"
        mixal_code += "        HLT\n"
        mixal_code += "ENDMSG ALF     END\n"
        return mixal_code

    def find_variables(self, ast):
        """Traverses the AST and returns a set of all variable names used."""
        variables = set()
        for statement in ast:
            if isinstance(statement, AssignNode):
                variables.add(statement.var)
            elif isinstance(statement, ReadNode):
                variables.add(statement.var)
            # Add other statement types (if needed) that might use variables
        return variables

    def generate_statement(self, node):
        if isinstance(node, AssignNode):
            return self.generate_assign(node)
        elif isinstance(node, IfNode):
            return self.generate_if(node)
        elif isinstance(node, RepeatNode):
            return self.generate_repeat(node)
        elif isinstance(node, ReadNode):
            return self.generate_read(node)
        elif isinstance(node, WriteNode):
            return self.generate_write(node)
        else:
            raise SyntaxError(f"Unknown AST node type: {type(node)}")

    def generate_assign(self, node):
        mixal_code = self.generate_expression(node.value)
        mixal_code += (
            f"        STA     {node.var.upper()}\n"  # Uppercase variable in STA
        )
        return mixal_code

    def generate_if(self, node):
        else_label = self.new_label()
        end_label = self.new_label()

        mixal_code = self.generate_expression(node.condition)
        mixal_code += f"        JZE     {else_label}\n"
        for stmt in node.then_branch:
            mixal_code += self.generate_statement(stmt)
        mixal_code += f"        JMP     {end_label}\n"
        mixal_code += f"{else_label}  "
        if node.else_branch:
            for stmt in node.else_branch:
                mixal_code += self.generate_statement(stmt)
        mixal_code += f"{end_label}   NOP\n"
        return mixal_code

    def generate_repeat(self, node):
        loop_start = self.new_label()
        loop_end = self.new_label()

        mixal_code = f"{loop_start}   NOP\n"
        for stmt in node.body:
            mixal_code += self.generate_statement(stmt)
        mixal_code += self.generate_expression(node.condition)
        mixal_code += f"        JNE     {loop_start}\n"
        mixal_code += f"{loop_end}   NOP\n"
        return mixal_code

    def generate_read(self, node):
        return f"""IN      1,1(0)    * Read input into register A
        JBUS    *(18)             * Wait until input is ready
        STA     {node.var.upper()}\n"""  # Uppercase variable in STA

    def generate_write(self, node):
        return f"        OUT     {node.var.upper()},2\n"  # Uppercase variable in OUT

    def generate_expression(self, node):
        if isinstance(node, BinaryOpNode):
            return self.generate_binary_op(node)
        elif isinstance(node, NumberNode):
            return f"        LDA     {node.value}\n"  # Correctly handles constants
        elif isinstance(node, IdNode):
            return f"        LDA     {node.name.upper()}\n"
        else:
            raise SyntaxError(f"Unknown expression node type: {type(node)}")

    def generate_binary_op(self, node):
        # Optimization: For commutative operations, try to load the right operand into A first
        if node.operator in ("PLUS", "MULTIPLY"):
            mixal_code = self.generate_expression(node.right)
            mixal_code += "        STA     T1\n"
            mixal_code += self.generate_expression(node.left)
        else:
            mixal_code = self.generate_expression(node.left)
            mixal_code += "        STA     T1\n"
            mixal_code += self.generate_expression(node.right)

        if node.operator == "PLUS":
            mixal_code += "        ADD     T1\n"
        elif node.operator == "MINUS":
            mixal_code += "        SUB     T1\n"
        elif node.operator == "MULTIPLY":
            mixal_code += "        MUL     T1\n"
        elif node.operator == "DIVIDE":
            mixal_code += "        DIV     T1\n"
        elif node.operator == "LESS_THAN":
            mixal_code += "        CMP     T1\n"
            mixal_code += f"        JL      TRUE{self.label_counter}\n"
            mixal_code += "        LDA     #0\n"
            mixal_code += f"        JMP     END{self.label_counter}\n"
            mixal_code += f"TRUE{self.label_counter}   LDA     #1\n"
            mixal_code += f"END{self.label_counter}     NOP\n"
            self.label_counter += 1
        elif node.operator == "EQUALS":
            mixal_code += "        CMP     T1\n"
            mixal_code += f"        JE      TRUE{self.label_counter}\n"
            mixal_code += "        LDA     #0\n"
            mixal_code += f"        JMP     END{self.label_counter}\n"
            mixal_code += f"TRUE{self.label_counter}   LDA     #1\n"
            mixal_code += f"END{self.label_counter}     NOP\n"
            self.label_counter += 1
        else:
            raise SyntaxError(f"Unsupported binary operator: {node.operator}")

        return mixal_code
