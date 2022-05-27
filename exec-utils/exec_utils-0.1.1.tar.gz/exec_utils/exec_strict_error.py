class ExecStrictError(RuntimeError):
    exit_code: int
    stderr: str
    stdout: str

    def __init__(self, msg, stdout, stderr, exit_code):
        super().__init__(msg)
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
