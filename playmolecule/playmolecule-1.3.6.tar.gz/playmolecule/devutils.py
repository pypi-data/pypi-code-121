# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#

# Utilities necessary inside PM apps
from playmolecule.job import Job
import inspect
import os


def tarFolder(folder, outtar=None, arcname=""):
    import tarfile

    folder = os.path.abspath(folder)
    parentdir = os.path.dirname(folder)
    foldername = os.path.basename(folder)

    if outtar is None:
        outtar = os.path.join(parentdir, f"{foldername}.tar.gz")

    with tarfile.open(outtar, "w:gz") as tar:
        tar.add(folder, arcname=arcname)

    return outtar


def getJobId(configpath):
    """
    Returns the job id stored in the config file

    Parameters
    ----------
    configpath: str
        The file path for the config file

    Returns
    -------
    jobid: str
        The id of the job
    """
    import json

    jobId = json.load(open(configpath, "r"))["execid"]
    return jobId


def setAsCompleted(outdir):
    """
    Writes the sentinel for the complete job.

    Parameters
    ----------
    outdir: str
        The location where to write the sentinel file
    """
    writeSentinel("pmwsjob.done", outdir)


def setAsError(outdir):
    """
    Writes the sentinel for the error job.

    Parameters
    ----------
    outdir: str
        The location where to write the sentinel file
    """
    writeSentinel("pmwsjob.err", outdir)


def setAsSleep(outdir):
    """
    Writes the sentinel for the complete job.

    Parameters
    ----------
    outdir: str
        The location where to write the sentinel file
    """
    writeSentinel("pmwsjob.sleep", outdir)


def writeSentinel(fname, outfolder, message=None):
    """
    Writes a sentinel file. A message can be written in the file

    Parameters
    ----------
    fname: str
        The sentinel file name
    outfolder: str
        The location where to write the sentinel file
    message: str
        The text to write in the sentinel file

    """
    import yaml

    fout = os.path.join(outfolder, fname)

    f = open(fout, "w")
    if message is not None:
        if isinstance(message, dict):
            yaml.dump(message, f, default_flow_style=True)
        else:
            f.write("{}\n".format(message))
    f.close()


def basenameInputs(parser, args, prefix="."):
    """
    Returns the basename of the value for the file arguments
    Parameters
    ----------
    parser: argparse.ArgumentParser
        The argparse parser
    args: dict
        The dictionary of the arguments to inspect
    prefix: str
        The path prefix to apply to the basename
    Returns
    -------
    args: dict
        The dictionary of the arguments with the basename value (for files)
    """
    for action in parser._actions:
        if (
            action.metavar == "FILE"
        ):  # For DIRECTORY should not use basename but the equivalent
            value = args[action.dest]
            if value is None or value == "":
                continue
            if isinstance(value, list):
                tmp_args = []
                for v in value:
                    if v == "":
                        continue
                    bname = os.path.basename(v)
                    oname = os.path.join(prefix, bname)
                    tmp_args.append(oname)
                args[action.dest] = tmp_args
            else:
                bname = os.path.basename(value)
                tmponame = (
                    bname if bname != "" else os.path.normpath(value).split("/")[-1]
                )
                oname = os.path.join(prefix, tmponame)
                args[action.dest] = oname
    return args


def writeInputsOptionsLog(path, parser, varset, debug=False):
    """
    Writes a log file, in yml format file, reporting all the options used for the current simulations.
    Parameters
    ----------
    parser: argparse.ArgumentParser
        The argparse parser
    path: str
        The folder destination where to write the log
    varset: Namespace
        The namespace that contains all the options used
    debug: bool
        Set as True if you want to write the debug value
    """
    import yaml

    fname = os.path.join(path, "inopt.yml")
    options = {k: ("" if v is None else v) for k, v in vars(varset).items()}
    if options["outdir"].startswith("/data/out"):
        del options["outdir"]
    if options["scratchdir"].startswith("/data/scratch"):
        del options["scratchdir"]
    if not debug:
        del options["debug"]
    options = basenameInputs(parser, options, prefix="")

    with open(fname, "w") as outfile:
        yaml.dump(options, outfile, default_flow_style=False)


def writeInputsOptionsLog2(path, params):
    """
    Writes a log file, in yml format file, reporting all the options used for the current simulations.

    Parameters
    ----------
    path: str
        The folder destination where to write the log
    params: dict
        The dict that contains all the options used
    """
    import yaml

    fname = os.path.join(path, "inopt.yml")
    options = {k: ("" if v is None else v) for k, v in params.items()}
    if "outdir" in options and options["outdir"].startswith("/data/out"):
        del options["outdir"]
    if "scratchdir" in options and options["scratchdir"].startswith("/data/scratch"):
        del options["scratchdir"]

    with open(fname, "w") as outfile:
        yaml.dump(options, outfile, default_flow_style=False)


def zipdir(path, ziph):
    """
    Adds all the tree files of the folder passed into the zip file
    Parameters
    ----------
    path: str
        The path to add to the zip file
    ziph: zipfile.ZipFile
        The zipfile object
    """
    # ziph is zipfile handle
    for root, _, files in os.walk(path):
        for file in files:
            ziph.write(
                os.path.join(root, file),
                os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
            )


def zipit(dir_list, zip_name):
    """
    Creates the zip file with all the files and folder passed

    Parameters
    ----------
    dir_list: list
        The list of files and folders to zip
    zip_name: str
        The name of the zipfile
    """
    import zipfile

    zipf = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    for dir in dir_list:
        if os.path.isdir(dir):
            zipdir(dir, zipf)
        else:
            zipf.write(dir, os.path.basename(dir))
    zipf.close()


def unzipit(z, tmpdir="./tmp", overwrite=False, outdir=None):
    """
    Returns a list with the files in the zip file (when a zip). In alternative, a list with the passed file/folder

    Paramteres
    ----------
    z: str
        The path file

    Returns
    -------
    inps: list
        A list of the file in zip or the file/folder as unique item list
    """
    import zipfile
    import shutil
    from glob import glob

    if not zipfile.is_zipfile(z):
        return [z]
    tmpdir = os.path.normpath(tmpdir)
    os.makedirs(tmpdir, exist_ok=True)

    with zipfile.ZipFile(z, "r") as zip_file:
        zip_file.extractall(tmpdir)

    tmpinps = glob(tmpdir + "/*")
    if outdir is None:
        outdir = os.getcwd()

    inps = []
    for f in tmpinps:
        b = os.path.basename(f)
        o = os.path.join(outdir, b)
        if os.path.exists(o) and not overwrite:
            continue
        if os.path.exists(o) and overwrite and os.path.isdir(o):
            shutil.rmtree(o)
        if os.path.exists(o) and overwrite and os.path.isfile(o):
            os.remove(o)
        shutil.move(f, o)
        inps.append(o)
    shutil.rmtree(tmpdir)

    return inps


def pmtryexcept(arg1, arg2, arg3):
    """
    The decorator that handles the try/except by redirecting the sys.stderr and sys.stdout to a log file.
    Two boolean arguments can trigger the usage of the log file: arg1 refers to standalone mode; arg2 refers to
    debug mode. For writing to the log file the arg1 needs to be False or the arg2 needs to be True.

    """
    import sys
    import traceback

    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            standalone = getattr(self, arg1)
            debug = getattr(self, arg2)
            pmwsjob = getattr(self, arg3)

            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                err_detail = "\nError detailed:\n\t{}: {}\n".format(type(e).__name__, e)
                tb = repr(traceback.extract_tb(e.__traceback__, limit=-1))
                _fr = tb.split()
                _file = _fr[_fr.index("file") + 1]
                _line = _fr[_fr.index("line") + 1]
                eType, eValue, eTraceback = sys.exc_info()
                summary_error = (
                    "Error raised from:\n\tfile: {}\n\tline: {}\n\ttype: {}\n\tvalue: {}\n\t"
                    "traceback {}\n".format(_file, _line, eType, eValue, eTraceback)
                )

                log = "" if standalone else "LOG"
                h1 = "# ERROR {}\n".format(log)
                h2 = "\n# Error summary (dev)\n"
                h3 = "\n# Error Traceback (dev)\n"
                spacer = "_" * 40

                if standalone and not debug:
                    text = [h2, summary_error, spacer, h3]
                    print("".join(text))
                    traceback.print_tb(e.__traceback__)
                    text = ["\n", spacer, "\n", h1, err_detail]
                    print("".join(text))
                else:
                    error_log = (
                        "/data/out/outerror.log" if not debug else "outerror.log"
                    )
                    flog = open(error_log, "w")
                    text = [h1, err_detail, spacer, h2, summary_error, spacer, h3]
                    flog.write("".join(text))
                    traceback.print_tb(e.__traceback__, file=flog)

                    flog.close()
                    if pmwsjob is not None:
                        setAsError("/data/out/")
                        # pmwsjob.setError()
                    print("Error !!!")
                sys.exit(0)

        return wrapped_f

    return wrap


########### New devutils for function-based singularity apps ##############
def _pm_try_except(func, SESSION, JOB, standalone, debug, vars):
    import traceback
    import sys

    try:
        func(SESSION, JOB, vars.outdir, vars.scratchdir, vars)
    except Exception as e:
        err_detail = f"\nError detailed:\n\t{type(e).__name__}: {e}\n"
        tb = repr(traceback.extract_tb(e.__traceback__, limit=-1))
        _fr = tb.split()
        _file = _fr[_fr.index("file") + 1]
        _line = _fr[_fr.index("line") + 1]
        eType, eValue, eTraceback = sys.exc_info()
        summary_error = f"Error raised from:\n\tfile: {_file}\n\tline: {_line}\n\ttype: {eType}\n\tvalue: {eValue}\n\t traceback {eTraceback}\n"

        h1 = "# ERROR LOG\n"
        h2 = "\n# Error summary (dev)\n"
        h3 = "\n# Error Traceback (dev)\n"
        spacer = "_" * 40

        if standalone and not debug:
            text = [h2, summary_error, spacer, h3]
            print("".join(text))
            traceback.print_tb(e.__traceback__)
            text = ["\n", spacer, "\n", h1, err_detail]
            print("".join(text))
        else:
            error_log = os.path.join(vars.outdir, "outerror.log")
            with open(error_log, "w") as flog:
                text = [h1, err_detail, spacer, h2, summary_error, spacer, h3]
                flog.write("".join(text))
                traceback.print_tb(e.__traceback__, file=flog)

            if JOB is not None:
                setAsError("/data/out/")
            print(f"Error !!! Check {error_log} for more details.")
        sys.exit(0)


def app_wrapper(args, parser, func):
    from playmolecule import Session
    import argparse

    standalone = True
    SESSION = None
    JOB = None

    if args.debug:
        standalone = False

    if len(args.token) > 0:
        SESSION = Session(token=args.token)
        JOB = SESSION.get_job(execid=getJobId("/data/in/config"))
        standalone = False

    # Convert empty strings to Nones
    args = vars(args)
    for arg, value in args.items():
        if value == "":
            args[arg] = None
    args = argparse.Namespace(**args)
    # ------------------------------

    os.makedirs(args.outdir, exist_ok=True)
    os.makedirs(args.scratchdir, exist_ok=True)

    writeInputsOptionsLog(args.outdir, parser, args, args.debug)

    _pm_try_except(func, SESSION, JOB, standalone, args.debug, args)

    if not standalone:
        # set the complete status of the job
        setAsCompleted(args.outdir)


def _write_argparser_json(outfile, parser, baseparser=None):
    from collections import OrderedDict
    from pathlib import Path
    import json

    def convertType(arg):
        try:
            argType = arg.type().__class__.__name__
            argType = "string" if argType == "str" else argType
        except Exception:
            argType = "bool"

        if arg.type == Path or (arg.metavar == "FILE" and argType == "string"):
            argType = "file"

        return argType

    parserargs = []
    tag_strings = []
    parseractions = parser._actions
    if baseparser is not None:
        parseractions += baseparser._actions

    for action in parseractions:
        # skip the hidden arguments, the excluded args and the help argument
        if action.help == "==SUPPRESS==" or action.dest in ("help",):
            continue
        actiondict = OrderedDict()
        actiondict["mandatory"] = action.required
        actiondict["type"] = convertType(action)

        actiondict["name"] = action.dest
        actiondict["value"] = "" if action.default is None else str(action.default)
        actiondict["tag"] = action.option_strings[-1]
        actiondict["description"] = action.help

        parserargs.append(actiondict)
        if actiondict["type"] == "string":
            tag_strings.append(actiondict["tag"])

    manifest = OrderedDict()
    manifest["description"] = parser.description
    manifest["params"] = parserargs

    with open(outfile, "w") as f:
        json.dump(manifest, f, indent=4)


def _handle_error(msg, JOB: Job, errorfile, exit=True):
    import sys
    import traceback

    if JOB is not None:
        if errorfile is not None:
            with open(errorfile, "a") as f:
                f.write(msg + "\n")
                traceback.print_exc(file=f)
        JOB._set_error(msg)
        if exit:
            sys.exit(1)
    else:
        print(msg)
        traceback.print_exc()


def _fancy_error_formatting(e):
    import traceback
    import sys

    err_detail = f"\nError detailed:\n\t{type(e).__name__}: {e}\n"
    tb = repr(traceback.extract_tb(e.__traceback__, limit=-1))
    _fr = tb.split()
    _file = _fr[_fr.index("file") + 1]
    _line = _fr[_fr.index("line") + 1]
    eType, eValue, eTraceback = sys.exc_info()
    summary_error = f"Error raised from:\n\tfile: {_file}\n\tline: {_line}\n\ttype: {eType}\n\tvalue: {eValue}\n\t traceback {eTraceback}\n"

    h1 = "# ERROR LOG\n"
    h2 = "\n# Error summary (dev)\n"
    h3 = "\n# Error Traceback (dev)\n"
    spacer = "_" * 40

    text = [h1, err_detail, spacer, h2, summary_error, spacer, h3]
    return "".join(text)


def _get_session(token, execid):
    from playmolecule import Session, JobStatus

    SESSION = None
    JOB = None
    EXECID = None
    if len(token) != 0:
        try:
            EXECID = execid
            SESSION = Session(token)
            JOB = SESSION.get_job(execid=execid)
            status = JOB.get_status()
            if status == JobStatus.RUNNING:
                raise RuntimeError(
                    "Found another job under the same execution ID currently running. Exiting to avoid race conditions."
                )
            JOB._set_start()
        except Exception as e:
            _handle_error(
                f"Wrapper failed to initialize session with error: {e}", JOB, None
            )
    return SESSION, JOB, EXECID


def app_wrapper2(func, cli_arg_str):
    from contextlib import redirect_stdout, redirect_stderr
    import importlib
    import datetime
    import shutil
    from unittest import mock
    import json
    from playmolecule import plac
    from pathlib import Path
    import yaml
    import traceback

    baseparser = app_arg_parser2("app")
    cli_arg = cli_arg_str.split()
    baseargs, _ = baseparser.parse_known_args(cli_arg)

    has_token = len(baseargs.token) != 0

    SESSION, JOB, EXECID = _get_session(baseargs.token, baseargs.execid)

    try:
        # Prepare app folders
        indir = "/data/in" if has_token else None
        outdir = "/data/out" if has_token else baseargs.outdir
        scratchdir = "/data/scratch" if has_token else baseargs.scratchdir
        errorfile = os.path.join(outdir, "pmwsjob.err")
        # TODO: Deprecate completedfile and sleepfile
        completedfile = os.path.join(outdir, "pmwsjob.done")
        sleepfile = os.path.join("/data", "pmwsjob.sleep")
        logfile = os.path.join(outdir, "log.txt")
        if indir is not None:
            os.makedirs(indir, exist_ok=True)
        os.makedirs(outdir, exist_ok=True)
        os.makedirs(scratchdir, exist_ok=True)
    except Exception as e:
        _handle_error(f"Failed at initializing wrapper with error {e}", JOB, None)
        return

    # Import the module/function of the app to call
    try:
        pieces = func.split(".")
        module = ".".join(pieces[:-1])
        func = getattr(importlib.import_module(module), pieces[-1])
    except Exception as e:
        _handle_error(
            f"Failed at importing module {func} with error {e}", JOB, errorfile
        )
        return

    # Download app inputs and input arguments from backend
    if JOB is not None:
        try:
            JOB._download("input", indir)
            JOB._download("output", outdir)

            config_file = os.path.join(indir, "config")
            shutil.move(JOB._download("config", "/data/"), config_file)
            params = json.load(open(config_file, "rb"))["params"]
            _download_datacenter_args(params, indir, SESSION)
            cli_arg = _parse_input_args(params, indir, outdir, scratchdir)
        except Exception as e:
            _handle_error(
                f"Wrapper failed to initialize session with error: {e}", JOB, errorfile
            )
            return

    try:
        # Parse the app args (CLI or backend)
        parser = plac.parser_from(func)
        if len(baseargs.dump_argparser):
            _write_argparser_json(baseargs.dump_argparser, parser, baseparser)
            return

        print("Parsing arguments", cli_arg)
        with mock.patch("sys.exit") as m:
            appargs, unknownargs = parser.parse_known_args(cli_arg)
            if len(unknownargs):
                # Check if the unknown args are known to the base parser
                _, unknownargs = baseparser.parse_known_args(unknownargs)
                if len(unknownargs):
                    # Otherwise throw an error for unknown arguments
                    parser.print_help()
                    raise RuntimeError(
                        f"Unrecognized arguments \"{' '.join(unknownargs)}\""
                    )
            if m.call_count > 0:
                raise RuntimeError("Failed parsing app arguments")
        kwargs = vars(appargs)

        # Convert empty strings to Nones
        for arg, value in kwargs.items():
            if value == "":
                kwargs[arg] = None
            if isinstance(value, Path):
                kwargs[arg] = str(value)

        # Override parsed outdir/scratchdir and write options to file
        if "outdir" in kwargs:
            kwargs["outdir"] = outdir
        if "scratchdir" in kwargs:
            kwargs["scratchdir"] = scratchdir
        writeInputsOptionsLog2(outdir, kwargs)
    except Exception as e:
        _handle_error(f"Unexpected error occurred in wrapper: {e}", JOB, errorfile)
        return

    sessionargs = {}
    sig = inspect.signature(func)
    if "_job" in sig.parameters:
        sessionargs["_job"] = JOB
    if "_session" in sig.parameters:
        sessionargs["_session"] = SESSION

    # Call app: simple CLI case
    if JOB is None:
        func(**sessionargs, **kwargs)
        return

    # Call app: running from backend PMWS case
    try:
        errored = False
        msg = ""
        try:
            currtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Change the cwd eventually to scratchdir
            with open(logfile, "a", buffering=1) as logf:
                logf.write(
                    f"\n#############\nExecuting {JOB._appid} {func} on {currtime}\nARGS:\n{yaml.dump(kwargs)}#############\n"
                )
                logf.flush()
                with redirect_stdout(logf), redirect_stderr(logf):
                    func(**sessionargs, **kwargs)
        except Exception as e:
            errored = True
            msg = _fancy_error_formatting(e)
            with open(errorfile, "a") as f:
                f.write(msg + "\n")
                traceback.print_exc(file=f)
        else:
            setAsCompleted(outdir)

        appname = baseargs.appname if len(baseargs.appname) else None
        # Get user-specified remote path for the results
        remotepath = None
        if len(baseargs.remotedir):
            remotepath = os.path.join(baseargs.remotedir, EXECID)
        if len(baseargs.remotepath):
            remotepath = baseargs.remotepath

        # TODO: Do I really need to re-upload the input???
        JOB._upload("input", indir, appname=appname)
        JOB._upload("output", outdir, appname=appname, remotepath=remotepath)
        # TODO: Get rid of flag files totally
        if errored:
            JOB._set_error(msg)
        elif os.path.exists(completedfile):
            JOB._set_complete()
        elif os.path.exists(sleepfile):
            os.remove(sleepfile)  # Can now be deleted before it's restarted
            JOB._set_sleep()
    except Exception as e:
        _handle_error(f"Unexpected error occurred in wrapper: {e}", JOB, errorfile)
        return


def app_arg_parser(description):
    import argparse

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-token",
        dest="token",
        action="store",
        type=str,
        default="",
        help=argparse.SUPPRESS,
    )
    # Override the app name for the wrapper uploads
    parser.add_argument(
        "-appname",
        dest="appname",
        action="store",
        type=str,
        default="",
        help="[DEV]: Allows overriding the application name. Use with caution.",
    )
    parser.add_argument(
        "-outdir",
        dest="outdir",
        action="store",
        type=str,
        default=".",
        help="The output folder where to write the results",
    )
    parser.add_argument(
        "-scratchdir",
        dest="scratchdir",
        action="store",
        type=str,
        default="scratch",
        help="The scratch folder where to write the temporary data",
    )
    parser.add_argument(
        "-remotedir",
        dest="remotedir",
        action="store",
        type=str,
        default="",
        help="[DEV]: A path to store the results in the backend. It will append the execid as a subfolder.",
    )
    parser.add_argument(
        "-remotepath",
        dest="remotepath",
        action="store",
        type=str,
        default="",
        help="[DEV]: A full path to store the results in the backend. Will not append the execid.",
    )
    parser.add_argument(
        "--debug", dest="debug", action="store_true", help=argparse.SUPPRESS
    )
    return parser


def app_arg_parser2(description):
    import argparse

    parser = argparse.ArgumentParser(description=description, add_help=False)
    parser.add_argument(
        "--token",
        dest="token",
        action="store",
        type=str,
        default="",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--execid",
        dest="execid",
        action="store",
        type=str,
        default="",
        help=argparse.SUPPRESS,
    )
    # Override the app name for the wrapper uploads
    parser.add_argument(
        "--appname",
        dest="appname",
        action="store",
        type=str,
        default="",
        help="[DEV]: Allows overriding the application name. Use with caution.",
    )
    parser.add_argument(
        "--outdir",
        dest="outdir",
        action="store",
        type=str,
        default=".",
        help="The output folder where to write the results",
    )
    parser.add_argument(
        "--scratchdir",
        dest="scratchdir",
        action="store",
        type=str,
        default="scratch",
        help="The scratch folder where to write the temporary data",
    )
    parser.add_argument(
        "--remotedir",
        dest="remotedir",
        action="store",
        type=str,
        default="",
        help="[DEV]: A path to store the results in the backend. It will append the execid as a subfolder.",
    )
    parser.add_argument(
        "--remotepath",
        dest="remotepath",
        action="store",
        type=str,
        default="",
        help="[DEV]: A full path to store the results in the backend. Will not append the execid.",
    )
    parser.add_argument(
        "--dump-argparser",
        dest="dump_argparser",
        type=str,
        default="",
        help=argparse.SUPPRESS,
    )
    return parser


# -------------- Used for building apps --------------
def _rebase_file(value, indir):
    def _rebase(v):
        if v.startswith(indir):
            return v
        if v.endswith("/"):
            v = v[:-1]
        return os.path.join(indir, os.path.basename(v))

    if isinstance(value, list):
        value = [_rebase(v) for v in value if v != ""]
    else:
        value = _rebase(value)
    return value


def _parse_input_args(params, indir, outdir, scratchdir):
    from distutils.util import strtobool

    input_args = []
    for param in params:
        name, value, dtype, tag = (
            param["name"],
            param["value"],
            param["type"],
            param["tag"],
        )
        # Empty or None arg
        if value is None or value == "" and name not in ("outdir", "scratchdir"):
            continue

        if dtype == "bool":
            if strtobool(value):  # if true
                input_args.append(tag)
        else:
            # Override directories
            if name == "outdir":
                value = outdir
            elif name == "scratchdir":
                value = scratchdir
            elif dtype == "file":
                value = _rebase_file(value, indir)

            input_args += [tag, str(value)]
    return input_args


def _download_datacenter_args(params, indir, session):
    from playmolecule import Dataset

    # We can pass a DataCenter ID instead of a file as an argument to a job and here we download it.
    for param in params:
        if isinstance(param["value"], str) and param["value"].startswith("dc://"):
            ds = Dataset(param["value"], _session=session)
            dl_dir = os.path.join(indir, str(ds.datasetid))
            param["value"] = ds.download(dl_dir)


def pmws_wrapper(token, execid, pythonexe):
    from playmolecule import Session, JobStatus
    import subprocess
    import traceback
    import datetime
    import shutil
    import json
    import sys

    indir = "/data/in"
    outdir = "/data/out"
    scratchdir = "/data/scratch"
    errorfile = os.path.join(outdir, "pmwsjob.err")
    completedfile = os.path.join(outdir, "pmwsjob.done")
    sleepfile = os.path.join("/data", "pmwsjob.sleep")
    logfile = os.path.join(outdir, "log.txt")

    try:
        session = Session(token)
        job = session.get_job(execid=execid)
    except Exception as e:
        with open(errorfile, "a") as f:
            f.write(f"Wrapper failed to initialize session with error: {e}\n")
            traceback.print_exc(file=f)
        sys.exit(1)

    try:
        os.makedirs(indir, exist_ok=True)
        os.makedirs(outdir, exist_ok=True)
        os.makedirs(scratchdir, exist_ok=True)

        status = job.get_status()
        if status == JobStatus.RUNNING:
            print(
                "Found another job under the same execution ID currently running. Exiting to avoid race conditions."
            )
            sys.exit(0)

        job._set_start()

        job._download("input", indir)
        job._download("output", outdir)

        config_file = os.path.join(indir, "config")
        shutil.move(job._download("config", "/data/"), config_file)
        params = json.load(open(config_file, "rb"))["params"]

        # Override the real appname
        appname = None
        for param in params:
            if param["name"] == "appname" and len(param["value"].strip()):
                appname = param["value"]

        _download_datacenter_args(params, indir, session)

        cmd = [pythonexe, "/logic/app.py", "-token", token]
        cmd = cmd + _parse_input_args(params, indir, outdir, scratchdir)
        currtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            # Change the cwd eventually to scratchdir
            with open(logfile, "a") as logf:
                logf.write(
                    f"\n#############\nExecuting {job._appid} on {currtime}\nCMD: {cmd}\n#############\n"
                )
                logf.flush()
                _ = subprocess.run(
                    cmd, stdout=logf, stderr=logf, check=True, cwd=outdir
                )
        except subprocess.CalledProcessError as e:
            with open(errorfile, "a") as f:
                f.write(f"===== App failed with error ======\n{e}")

        # TODO: Do I really need to re-upload the input???
        job._upload("input", indir, appname=appname)
        # Get user-specified remote path for the results
        remotepath = None
        for param in params:
            if param["name"] == "remotepath" and len(param["value"].strip()):
                remotepath = os.path.join(param["value"], execid)
                break
        job._upload("output", outdir, appname=appname, remotepath=remotepath)

        if os.path.exists(completedfile):
            job._set_complete()
        elif os.path.exists(errorfile):
            job._set_error()
        elif os.path.exists(sleepfile):
            os.remove(sleepfile)  # Can now be deleted before it's restarted
            job._set_sleep()
    except Exception as e:
        with open(errorfile, "a") as f:
            f.write(f"Unexpected error occurred in wrapper: {e}\n")
            traceback.print_exc(file=f)

        try:
            job._set_error()
        except:
            pass
