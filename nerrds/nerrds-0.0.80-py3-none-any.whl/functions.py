


def check_quiet_print(quiet,msg,end='\n'):
    out = open('NERRDS.log','a+')
    out.write(msg+end)
    out.close()
    if not quiet:
        print(msg,end=end)
