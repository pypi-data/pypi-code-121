


def check_quiet_print(quiet,msg,end='\n'):
    out = open('NERRDS.log','a+')
    out.write(msg+end)
    out.close()
    if not quiet:
        print(msg,end=end)

def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout