import sys

def eval_expr(*args):
    if len(args) == 0:
        return "Empty expression..."
    else:
        try:
            expr = ' '.join(args)
            return eval(expr)
        except SyntaxError:
            print("Illegal expression: " + expr)
            sys.exit(1)
