from .imports import * 

def tee_output(file):
    tee = subprocess.Popen(["tee", file], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno()) # type: ignore
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno()) # type: ignore