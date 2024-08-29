# ast_node.py


class ASTNode:
    def print_node(self, indent=0):
        print("  " * indent + self.__class__.__name__)
        for attr in vars(self):
            value = getattr(self, attr)
            if isinstance(value, ASTNode):
                print("  " * (indent + 1) + f"{attr}:")
                value.print_node(indent + 2)
            elif isinstance(value, list):  # Handle lists of ASTNodes
                print("  " * (indent + 1) + f"{attr}:")
                for item in value:
                    item.print_node(indent + 2)
            else:
                print("  " * (indent + 1) + f"{attr}: {value}")


class AssignNode(ASTNode):
    def __init__(self, var, value):
        self.var = var
        self.value = value


class IfNode(ASTNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class RepeatNode(ASTNode):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition


class ReadNode(ASTNode):
    def __init__(self, var):
        self.var = var


class WriteNode(ASTNode):
    def __init__(self, var):
        self.var = var


class BinaryOpNode(ASTNode):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


class IdNode(ASTNode):
    def __init__(self, name):
        self.name = name
