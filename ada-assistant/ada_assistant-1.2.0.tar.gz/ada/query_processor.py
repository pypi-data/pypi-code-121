from ada import query_calc
from ada import query_memory
from ada import query_show
from ada import query_time

def process_query(args):
    if 'calc' in args:
        print(query_calc.eval_expr(*args[args.index('calc')+1:]))
    elif 'show' in args:
        query_show.process_show(*args[args.index('show')+1:])
    elif 'peek' in args or 'remember' in args or 'register' in args or 'forget' in args or 'config' in args or 'amend' in args or 'append' in args or 'pwd' in args:
        query_memory.process_memory(*args)
    elif "help" in args or "--help" in args:
        query_show.process_show("help")
    else:
        query_time.process_time_query(*args)
