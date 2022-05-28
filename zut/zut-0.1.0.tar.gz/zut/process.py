import logging
from operator import lt
import sys
import subprocess, shlex
from pathlib import Path
from collections import namedtuple
from .color import FOREGROUND_GRAY, FOREGROUND_RED

logger = logging.getLogger(__name__)


def _decode_output(bytes, codecs=['utf8', 'cp1252']):
    if not bytes:
        return ""
    
    for codec in codecs:
        try:
            decoded = bytes.decode(codec).strip()
            if not decoded:
                return ""
            return decoded
        except UnicodeDecodeError:
            pass

    logging.warning("cannot decode command output using %s", codecs)
    return str(bytes)


CallResult = namedtuple("CallResult", ["returncode", "stdout", "stderr"])

class CallResultError(ValueError):
    def __init__(self, logcmd, message, result: CallResult) -> None:
        self.returncode = result.returncode
        self.stdout = result.stdout
        self.stderr = result.stderr
        super().__init__("%s %s" % (logcmd, message))


def call(cmd, input=None, as_superuser=False, on_failure="raise", accept_nonzero=False, accept_stderr=False, accept_stdout=True, log=False) -> CallResult:
    # Prepare arguments
    args = [str(arg) for arg in cmd] if isinstance(cmd, list) else shlex.split(cmd)
    if not args:
        raise ValueError("no command provided")
    loglabel = log if log and isinstance(log, str) else Path(args[0]).name

    if as_superuser:
        if sys.platform == "win32":
            args = ["powershell.exe", "Start-Process", args[0], "-Verb", "runAs", "-ArgumentList"]
            for i, arg in enumerate(args[1:]):
                if i > 0:
                    args.append(",")
                args.append("\"%s\"" % arg.replace("\"", "\\\""))
        else:
            args = ["sudo"] + args

    # Run process
    res = subprocess.run(args, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Analyze result
    result = CallResult(res.returncode, _decode_output(res.stdout), _decode_output(res.stderr))

    failure = False
    message = ""

    if result.returncode != 0:
        if not (accept_nonzero == True or accept_nonzero == res.returncode or (isinstance(accept_nonzero, list) and res.returncode in accept_nonzero)):
            failure = True
            message += ("\n" if message else "") + f"returncode: {FOREGROUND_RED}" % result.returncode
        elif log:
            message += ("\n" if message else "") + f"returncode: {FOREGROUND_GRAY}" % result.returncode

    if result.stderr:
        if not accept_stderr:
            failure = True
            message += ("\n" if message else "") + f"stderr: {FOREGROUND_RED}" % result.stderr
        elif log:
            message += ("\n" if message else "") + f"stderr: {FOREGROUND_GRAY}" % result.stderr

    if result.stdout:
        if not accept_stdout:
            failure = True
            message += ("\n" if message else "") + f"stdout: {FOREGROUND_RED}" % result.stdout
        elif log:
            # optimize logging: if there is nothing else than stdout, do not print "stdout: "
            if message:
                message += f"\nstdout: {FOREGROUND_GRAY}" % result.stdout
            else:
                message = FOREGROUND_GRAY % result.stdout

    if message:
        if failure:
            on_failure = on_failure.lower()
            if on_failure in ["error", "log_error"]:
                logger.error("%s: %s", loglabel, message)
            elif on_failure in ["warning", "warn", "log_warning", "log_warn", "log"]:
                logger.warning("%s: %s", loglabel, message)
            elif on_failure:
                raise CallResultError(loglabel, message, result)
        else:
            logger.info("%s: %s", loglabel, message)
    elif log:
        logger.info("%s: %s", loglabel, FOREGROUND_GRAY % "done")

    return result


def call_returncode(cmd, input=None, as_superuser=False, on_failure="raise", accept_nonzero=False, accept_stderr=False, accept_stdout=True, log=False) -> int:
    """
    Call a process and return output.
    """
    result = call(cmd, input=input, as_superuser=as_superuser, on_failure=on_failure, accept_nonzero=accept_nonzero, accept_stderr=accept_stderr, accept_stdout=accept_stdout, log=log)
    return result.returncode


def call_output(cmd, input=None, as_superuser=False, on_failure="raise", accept_nonzero=False, accept_stderr=False, accept_stdout=True, include_stderr=False, include_stdout=True, log=False) -> str:
    """
    Call a process and return output.
    """
    result = call(cmd, input=input, as_superuser=as_superuser, on_failure=on_failure, accept_nonzero=accept_nonzero, accept_stderr=accept_stderr, accept_stdout=accept_stdout, log=log)
    
    output = ""
    if result.stderr and include_stderr:
        output += ("\n" if output else "") + result.stderr
    if result.stdout and include_stdout:
        output += ("\n" if output else "") + result.stdout
    return output
