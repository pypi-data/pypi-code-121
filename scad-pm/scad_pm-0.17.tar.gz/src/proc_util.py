import subprocess


def call(cwd, process_with_params, throw_on_error=True):
    ret_code = subprocess.call(process_with_params, cwd=cwd)
    if throw_on_error and ret_code != 0:
        raise Exception("Error executing[{}]: {}".format(cwd, process_with_params))
    return ret_code
