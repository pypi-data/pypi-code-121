import os
import subprocess


# TODO(mattweber): Once this code has been deployed in a CLI release
# that we can expect to be available on product clusters, migrate all
# use of _run_kill_child to this function.
def run_kill_child(
    *popenargs, input=None, timeout=None, check=False, **kwargs
) -> subprocess.CompletedProcess:
    return _run_kill_child(
        *popenargs, input=input, timeout=timeout, check=check, **kwargs
    )


# TODO(mattweber): This is a public function despite the underscore.
# Renaming this function in this PR is problematic for setup_dev_ray in
# config_controller because it needs to import this function
# for use in a remote function.
def _run_kill_child(
    *popenargs, input=None, timeout=None, check=False, **kwargs
) -> subprocess.CompletedProcess:
    """
    This function is a fork of subprocess.run with fewer args.
    The goal is to create a child subprocess that is GUARANTEED to exit when the parent exits
    This is accomplished by:
    1. Making sure the child is the head of a new process group
    2. Create a third "Killer" process that is responsible for killing the child when the parent dies
    3. Killer process checks every second if the parent is dead.
    4. Killing the entire process group when we want to kill the child

    Arguments are the same as subprocess.run
    """
    # Start new session ensures that this subprocess starts as a new process group
    with subprocess.Popen(start_new_session=True, *popenargs, **kwargs) as process:
        parent_pid = os.getpid()
        child_pid = process.pid
        child_pgid = os.getpgid(child_pid)

        # Open a new subprocess to kill the child process when the parent process dies
        # kill -s 0 parent_pid will succeed if the parent is alive.
        # If it fails, SIGKILL the child process group and exit
        subprocess.Popen(
            f"while kill -s 0 {parent_pid}; do sleep 1; done; kill -9 -{child_pgid}",
            shell=True,
            # Suppress output
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except:  # noqa      (this is taken from subprocess.run directly)
            # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() as .__exit__ does that for us.
            raise

        retcode = process.poll()
        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode, process.args, output=stdout, stderr=stderr
            )
    return subprocess.CompletedProcess(process.args, retcode or 0, stdout, stderr)
