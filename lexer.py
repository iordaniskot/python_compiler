#lexer.py
import re

token_patterns = [
    (r'\bif\b', 'IF'),
    (r'\bthen\b', 'THEN'),
    (r'\belse\b', 'ELSE'),
    (r'\bend\b', 'END'),
    (r'\brepeat\b', 'REPEAT'),
    (r'\buntil\b', 'UNTIL'),
    (r'\bwrite\b', 'WRITE'),
    (r'\bread\b', 'READ'),
    (r'\b[0-9]+\b', 'NUMBER'),
    (r'\b[a-zA-Z_][a-zA-Z_0-9]*\b', 'ID'),
    (r'\:=', 'ASSIGN'),
    (r'\+', 'PLUS'),
    (r'\-', 'MINUS'),
    (r'\*', 'MULTIPLY'),
    (r'\/', 'DIVIDE'),
    (r'\<', 'LESS_THAN'),
    (r'\>', 'GREATER_THAN'),
    (r'\!', 'NOT'),
    (r'\&', 'AND'),
    (r'\|', 'OR'),
    (r'\=', 'EQUALS'),
    (r'\;', 'SEMICOLON'),
    (r'\(', 'LPAREN'),
    (r'\)', 'RPAREN'),
    (r'\s+', None),  # Ignore whitespace
]

# Tokenizer function
def tokenize(source_code):
    tokens = []
    while source_code:
        match = None
        for pattern, token_type in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(source_code)
            if match:
                if token_type:  # Ignore whitespace
                    tokens.append((match.group(0), token_type))
                source_code = source_code[match.end():]
                break
        if not match:
            raise SyntaxError("Invalid token")
    return tokens
