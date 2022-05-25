import ply.yacc as yacc
import sys
from templo.lexer import tokens, literals
from templo.parser_error import *

precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("left", "NOT"),
    (  # Nonassociative operators
        "nonassoc",
        "EQ",
        "NE",
        "GT",
        "GE",
        "LT",
        "LE",
        "IS",
        "IN",
        "ISNOT",
        "NOTIN",
    ),
    ("left", "ADD", "SUB"),
    ("left", "MUL", "DIV", "FDIV", "RMD"),
    ("left", "POW"),
    ("right", "UMINUS", "UPLUS"),
    ("left", "CS"),
)


def p_Template(p):
    "Template : Elems"
    p[0] = p[1]


def p_Elems_multiple(p):
    "Elems : Elems Elem"
    p[0] = p[1] + [p[2]]


def p_Elems_single(p):
    "Elems :"
    p[0] = []


def p_Elem_TEXT(p):
    "Elem : text"
    p[0] = ("text", p[1])


def p_Elem_Code(p):
    "Elem : Code"
    p[0] = p[1]


def p_Code_Expression(p):
    "Code : Expression"
    p[0] = p[1]


def p_Code_Statement(p):
    "Code : Statement"
    p[0] = p[1]


def p_Expression(p):
    "Expression : OE Exp CE"
    p[0] = ("print", (p[2]))


def p_Statement_If(p):
    "Statement : If"
    p[0] = p[1]


def p_Statement_For(p):
    "Statement : For"
    p[0] = p[1]


def p_Statement_Repeat(p):
    "Statement : Repeat"
    p[0] = p[1]


def p_If(p):
    "If : OS IF Exp CS Elems OS ENDIF CS"
    p[0] = ("if", [(p[3], p[5])])


def p_If_else(p):
    "If : OS IF Exp CS Elems OS ELSE CS Elems OS ENDIF CS"
    p[0] = ("if", [(p[3], p[5]), (("bool", "True"), p[9])])


def p_If_elifs(p):
    "If : OS IF Exp CS Elems Elifs OS ENDIF CS"
    p[0] = ("if", [(p[3], p[5])] + p[6])


def p_If_elifs_else(p):
    "If : OS IF Exp CS Elems Elifs OS ELSE CS Elems OS ENDIF CS"
    p[0] = ("if", [(p[3], p[5])] + p[6] + [(("bool", "True"), p[10])])


def p_Elifs_multiple(p):
    "Elifs : Elifs Elif"
    p[0] = p[1] + [p[2]]


def p_Elifs_single(p):
    "Elifs : Elif"
    p[0] = [p[1]]


def p_Elif(p):
    "Elif : OS ELIF Exp CS Elems"
    p[0] = (p[3], p[5])


def p_For(p):
    "For : OS FOR id IN id CS Elems OS ENDFOR CS"
    p[0] = ("for", p[3], p[5], p[7])


def p_For_dict(p):
    "For : OS FOR id ',' id IN id CS Elems OS ENDFOR CS"
    p[0] = ("fordict", p[3], p[5], p[7], p[9])


def p_Repeat(p):
    "Repeat : OS REPEAT Exp CS Elems OS ENDREPEAT CS"
    p[0] = ("repeat", p[3], p[5])


def p_Exp_id(p):
    "Exp : id"
    p[0] = ("variable", p[1])


def p_Exp_Literal(p):
    "Exp : Literal"
    p[0] = p[1]


def p_Exp_types(p):
    """Exp : AExp
    Exp : RExp
    Exp : LExp
    Exp : OExp"""
    p[0] = p[1]


def p_Exp_braces(p):
    "Exp : '(' Exp ')'"
    p[0] = p[2]


def p_Literal_str(p):
    "Literal : str"
    p[0] = ("text", p[1][1:][:-1])


def p_Literal_Num(p):
    "Literal : Num"
    p[0] = p[1]


def p_Literal_Bool(p):
    "Literal : Bool"
    p[0] = p[1]


def p_Literal_List(p):
    "Literal : '[' List ']'"
    p[0] = ("list", p[2])


def p_List_multiple(p):
    "List : List ',' Exp"
    p[0] = p[1] + [p[3]]


def p_List_single(p):
    "List : Exp"
    p[0] = [p[1]]


def p_List_empty(p):
    "List :"
    p[0] = []


def p_Num_int(p):
    "Num : int"
    p[0] = ("int", p[1])


def p_Num_float(p):
    "Num : float"
    p[0] = ("float", p[1])


def p_Bool_TRUE(p):
    "Bool : TRUE"
    p[0] = ("bool", p[1])


def p_Bool_FALSE(p):
    "Bool : FALSE"
    p[0] = ("bool", p[1])


def p_AExp_bin(p):
    """AExp : Exp ADD Exp
    | Exp SUB Exp
    | Exp MUL Exp
    | Exp DIV Exp
    | Exp FDIV Exp
    | Exp RMD Exp
    | Exp POW Exp"""
    p[0] = (p[2], p[1], p[3])


def p_AExp_UMINUS(p):
    "AExp : SUB Exp %prec UMINUS"
    p[0] = ("uminus", p[2])


def p_AExp_UPLUS(p):
    "AExp : ADD Exp %prec UPLUS"
    p[0] = ("uplus", p[2])


def p_RExp_bin(p):
    """RExp : Exp EQ Exp
    | Exp NE Exp
    | Exp GT Exp
    | Exp GE Exp
    | Exp LT Exp
    | Exp LE Exp
    | Exp IS id
    | Exp IN Exp"""
    p[0] = (p[2], p[1], p[3])


def p_RExp_NOTIN(p):
    "RExp : Exp ISNOT id"
    p[0] = ("isnot", p[1], p[3])


def p_RExp_ISNOT(p):
    "RExp : Exp NOTIN Exp"
    p[0] = ("notin", p[1], p[3])


def p_LExp_NOT(p):
    "LExp : NOT Exp"
    p[0] = ("not", p[2])


def p_LExp_AND(p):
    "LExp : Exp AND Exp"
    p[0] = ("and", p[1], p[3])


def p_LExp_OR(p):
    "LExp : Exp OR Exp"
    p[0] = ("or", p[1], p[3])


def p_OExp_filter(p):
    "OExp : Exp PIPE id"
    p[0] = ("filter", p[1], p[3])


def p_OExp_attr(p):
    "OExp : Exp DOT id"
    p[0] = ("attr", p[1], p[3])


def p_OExp_item(p):
    "OExp : Exp '[' Exp ']'"
    p[0] = ("item", p[1], p[3])


def p_OExp_method(p):
    "OExp : Exp DOT id '(' Args ')'"
    p[0] = ("method", p[1], p[3], p[5])


def p_Args_multiple(p):
    "Args : Args ',' Exp"
    p[0] = p[1] + [p[3]]


def p_Args_single(p):
    "Args : Exp"
    p[0] = [p[1]]


def p_Args_empty(p):
    "Args :"
    p[0] = []


# Error rule for syntax errors
def p_error(p):
    print(f"Error at line {p.lineno}:")
    print("\tToken:", p.value)
    print("\tType:", p.type)


# Build the parser
parser = yacc.yacc(start="Template")
parser.success = True

def main(argv):
    import readline

    while True:
        parser.success = True
        try:
            s = input("template > ")
        except EOFError:
            break
        if not s:
            continue
        ast = parser.parse(s)
        if parser.success:
            print("ast:", ast)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
