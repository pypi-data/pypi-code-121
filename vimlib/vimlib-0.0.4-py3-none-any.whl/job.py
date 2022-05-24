""" WARNING: Incomplete

Should be moved to a branch (e.g. `jobs`)
"""
import vim


# pyvim.Job('flask run')
class Job:
    # See ~/.vim/plugin/jobs.vim
    """
    execute=...command/script/shell...
    shell=cmd/poweshell/py/ruby...
    buffer=...
    file=...
    handlers...
    """

    def __init__(
        self,
        status=None,
        cmd=None,
        stoponexit=None,
        tty_out=None,
        exitval=None,
        exit_cb=None,
        tty_in=None,
        channel=None,
        tty_type=None,
        process=None,
    ):

        self.status = status
        self.cmd = cmd
        self.stoponexit = stoponexit
        self.tty_out = tty_out
        self.exitval = exitval
        self.exit_cb = exit_cb
        self.tty_in = tty_in
        self.channel = channel
        self.tty_type = tty_type
        self.process = process

    def stop(self, how=None):

        # SUCCESS
        # Need to pass a Vim job object to it...
        process = self.process
        vim.command(
            '|'.join(
                f"""
        for job in job_info()
            if {process} == job_info(job)['process']
                call job_stop(job)
            endif
        endfor
        """.splitlines()
            )
        )


# {'status': 'run', 'cmd': ['cmd', '/c', 'py -m flask run'], 'stoponexit': 'term', 'tty_out': '', 'exitval': '0', 'exit_cb': '', 'tty_in': '', 'channel': None, 'tty_type': '', 'process': '11916'}
