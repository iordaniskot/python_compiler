# main.py

# Importing necessary components from other modules
from lexer import tokenize
from parser import Parser
from code_generator import CodeGenerator
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


def main():
    # Example source code written in the Simple Language
    source_code1 = """
    read x;
    if 0 < x then
      fact := 1;
      repeat
        fact := fact * x;
        x := x - 1
      until x = 0;
      write fact
    end
    """

    source_code2 = """
    read x;
    total := 3;
    total := total + x;
    write total
    """

    source_code3 = """
    read x;
    y := 4;
    
    if x<2 then
      write x
    else
      write y
    end
    """

    source_code4 = """
    i := 0;
    read x;
    if 2 < x then
        y := 3;
    else
        y := 4
    end
    """

    source_code5 = """
    x := 2;
    y := 4;
    
    total := x * y;
    write total
    """
    source_code6 = """
    i := 10;
    if 0 < i then
      repeat
        write i;
        i := i - 1
      until i = 0
    end
    """

    source_code = source_code6
    # Step 1: Tokenization
    try:
        tokens = tokenize(source_code)
        print("Tokens:")
        for token in tokens:
            print(token)
    except SyntaxError as e:
        print(f"Tokenization error: {e}")
        return

    # Step 2: Parsing
    try:
        parser = Parser(tokens)
        ast = parser.parse_program()
        print("\nAbstract Syntax Tree (AST):")
        for statement in ast:
            statement.print_node()
    except SyntaxError as e:
        print(f"Parsing error: {e}")
        return

    # Step 3: Code Generation
    code_generator = CodeGenerator()
    mixal_code = code_generator.generate(ast)

    # Step 4: Output the generated MIXAL code
    print("\nGenerated MIXAL Code:")
    print(mixal_code)


if __name__ == "__main__":
    main()
