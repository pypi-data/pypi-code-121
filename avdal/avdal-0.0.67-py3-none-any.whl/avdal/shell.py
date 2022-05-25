import json
import subprocess as proc


def run(cmd, *args, cwd=None, check=False):
    try:
        if cwd is not None and len(cwd.strip()) == 0:
            cwd = "."

        exec = proc.run([cmd] + [str(a) for a in args],
                        cwd=cwd,
                        stdout=proc.PIPE,
                        stderr=proc.PIPE,
                        universal_newlines=True)
    except Exception as err:
        if check:
            raise err
        return 1, str(err), ""

    if check and exec.returncode != 0:
        raise Exception(f"Command returned {exec.returncode}")

    return exec.returncode, exec.stdout, exec.stderr


def runj(cmd, *args, cwd=None, check=False):
    ret, stdout, stderr = run(cmd, *args, cwd=cwd, check=check)

    if ret != 0:
        ret, {"_stdout": stdout, "_stderr": stderr}

    try:
        return 0, json.loads(stdout)
    except json.JSONDecodeError as err:
        return 1, {"_decode_err": err, "_stdout": stdout, "_stderr": stderr}
