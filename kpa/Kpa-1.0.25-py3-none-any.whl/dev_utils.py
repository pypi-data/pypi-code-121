import time, random
from pathlib import Path
from functools import wraps

def run(filepath:str = '', make_cache:bool = True, run_rarely:bool = False) -> None:
    if run_rarely:
        seconds_since_last_change = time.time() - Path(filepath).stat().st_mtime
        if seconds_since_last_change > 30 and random.random() > 0.01:
            return  # Don't run
    run_flake8(filepath)
    run_mypy(filepath, make_cache=make_cache)

def run_flake8(filepath:str = '') -> None:
    import subprocess, sys
    p = subprocess.run(['flake8', '--show-source', '--ignore=E501,E302,E251,E701,E226,E305,E225,E261,E231,E301,E306,E402,E704,E265,E201,E202,E303,E124,E241,E127,E266,E221,E126,E129,F811,E222,E401,E702,E203,E116,E228,W504,W293,B007,W391,F401,W292,E227,E128', filepath])
    if p.returncode != 0: sys.exit(1)

def run_mypy(filepath:str = '', make_cache:bool = True) -> None:
    import subprocess, sys
    cmd = ['mypy', '--pretty', '--ignore-missing-imports']
    if not make_cache: cmd.append('--cache-dir=/dev/null')
    if filepath: cmd.append(filepath)
    p = subprocess.run(cmd)
    if p.returncode != 0: sys.exit(1)

