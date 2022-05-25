import ply.yacc as yacc
from templo.lexer import tokens, literals

def p_Template_error(p):
    "Template : error"
    print(f"Syntax error in template: Bad everything!")
    p.parser.success = False


def p_Expression_error(p):
    "Expression : OE error CE"
    print(f"Syntax error in expression block: Bad expression!")
    p.parser.success = False


def p_If_error(p):
    "If : OS IF error CS Elems OS ENDIF CS"
    print(f"Syntax error in if block: Bad expression!")
    p.parser.success = False


def p_If_else_error(p):
    "If : OS IF error CS Elems OS ELSE CS Elems OS ENDIF CS"
    print(f"Syntax error in if block: Bad expression!")
    p.parser.success = False


def p_If_elifs_error(p):
    "If : OS IF error CS Elems Elifs OS ENDIF CS"
    print(f"Syntax error in if block: Bad expression!")
    p.parser.success = False


def p_If_elifs_else_error(p):
    "If : OS IF error CS Elems Elifs OS ELSE CS Elems OS ENDIF CS"
    print(f"Syntax error in if block: Bad expression!")
    p.parser.success = False


def p_Elif_error(p):
    "Elif : OS ELIF error CS Elems"
    print(f"Syntax error in elif block: Bad expression!")
    p.parser.success = False


def p_For_error(p):
    "For : OS FOR error IN id CS Elems OS ENDFOR CS"
    print(f"Syntax error in for block: Bad id!")
    p.parser.success = False


def p_For_dict_error(p):
    "For : OS FOR error ',' id IN id CS Elems OS ENDFOR CS"
    print(f"Syntax error in for block: Bad id!")
    p.parser.success = False
