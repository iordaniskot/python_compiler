# parser.py

from ast_node import AssignNode, IfNode, RepeatNode, ReadNode, WriteNode, BinaryOpNode, NumberNode, IdNode

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens.pop(0) if self.tokens else None

    def parse_program(self):
        # Program ::= stmt_seq
        return self.parse_stmt_seq()

    def parse_stmt_seq(self):
        # stmt_seq ::= stmt_seq ; stmt | stmt
        statements = [self.parse_stmt()]
        while self.current_token and self.current_token[1] == 'SEMICOLON':
            self.next_token()
            statements.append(self.parse_stmt())
        return statements

    def parse_stmt(self):
        # Determine which type of statement to parse
        if self.current_token[1] == 'IF':
            return self.parse_if_stmt()
        elif self.current_token[1] == 'REPEAT':
            return self.parse_repeat_stmt()
        elif self.current_token[1] == 'ID':
            return self.parse_assign_stmt()
        elif self.current_token[1] == 'READ':
            return self.parse_read_stmt()
        elif self.current_token[1] == 'WRITE':
            return self.parse_write_stmt()
        else:
            raise SyntaxError("Invalid statement")

    def parse_if_stmt(self):
        # if_stmt ::= if exp then stmt_seq end | if exp then stmt_seq else stmt_seq end
        self.match('IF')
        condition = self.parse_exp()
        self.match('THEN')
        then_branch = self.parse_stmt_seq()
        if self.current_token[1] == 'ELSE':
            self.next_token()
            else_branch = self.parse_stmt_seq()
        else:
            else_branch = None
        self.match('END')
        return IfNode(condition, then_branch, else_branch)

    def parse_repeat_stmt(self):
        # repeat_stmt ::= repeat stmt_seq until exp
        self.match('REPEAT')
        body = self.parse_stmt_seq()
        self.match('UNTIL')
        condition = self.parse_exp()
        return RepeatNode(body, condition)

    def parse_assign_stmt(self):
        # assign_stmt ::= id := exp
        var_name = self.current_token[0]
        self.match('ID')
        self.match('ASSIGN')
        value = self.parse_exp()
        return AssignNode(var_name, value)

    def parse_read_stmt(self):
        # read_stmt ::= read exp
        self.match('READ')
        var_name = self.current_token[0]
        self.match('ID')
        return ReadNode(var_name)

    def parse_write_stmt(self):
        # write_stmt ::= write exp
        self.match('WRITE')
        var_name = self.current_token[0]
        self.match('ID')
        return WriteNode(var_name)

    def parse_exp(self):
        # Implement expression parsing based on grammar rules
        # exp ::= rel_exp
        return self.parse_rel_exp()

    def parse_rel_exp(self):
        # rel_exp ::= simple_exp | rel_exp < simple_exp | rel_exp = simple_exp
        left = self.parse_simple_exp()
        while self.current_token and self.current_token[1] in ('LESS_THAN', 'EQUALS'):
            op = self.current_token[1]
            self.next_token()
            right = self.parse_simple_exp()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_simple_exp(self):
        # simple_exp ::= term | simple_exp + term | simple_exp - term
        left = self.parse_term()
        while self.current_token and self.current_token[1] in ('PLUS', 'MINUS'):
            op = self.current_token[1]
            self.next_token()
            right = self.parse_term()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_term(self):
        # term ::= factor | term * factor | term / factor
        left = self.parse_factor()
        while self.current_token and self.current_token[1] in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token[1]
            self.next_token()
            right = self.parse_factor()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_factor(self):
        # factor ::= ( exp ) | number | id
        if self.current_token[1] == 'LPAREN':
            self.match('LPAREN')
            exp = self.parse_exp()
            self.match('RPAREN')
            return exp
        elif self.current_token[1] == 'NUMBER':
            value = int(self.current_token[0])
            self.match('NUMBER')
            return NumberNode(value)
        elif self.current_token[1] == 'ID':
            var_name = self.current_token[0]
            self.match('ID')
            return IdNode(var_name)
        else:
            raise SyntaxError("Invalid factor")

    def match(self, token_type):
        if self.current_token and self.current_token[1] == token_type:
            self.next_token()
        else:
            raise SyntaxError(f"Expected token {token_type}")
