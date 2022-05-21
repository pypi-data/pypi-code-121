import sys
import json
import subprocess


for line in sys.stdin:
    if not line:
        continue
    pargs, kwargs = json.loads(line)
    ret = subprocess.run(
        *pargs,
        stdin=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **kwargs
    )
    sys.stdout.write(
        json.dumps(dict(code=ret.returncode, out=ret.stdout, err=ret.stderr,)) + "\n"
    )
    sys.stdout.flush()
