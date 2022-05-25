"""
A python package to communicate with statistical software.

talk2stat allows programs (such as latextopdf, nodejs) to communicate with statistical packages. Currently, we connect with R, julia, matlab, or python but extending it to other tools like Stata or SAS, is very simple. The package contains two main functions: server() talks to the client program (e.g latextopdf) via a socket (inet), and to the stats package (R, julia, matlab, python) via a bi-directional pipe. The client() function is called by the user (e.g. latextopdf) to establish a connection with the server and pass code to the statistical package, and get the results.
"""
from configparser import ConfigParser
import pexpect
import sys
import os
import os.path
import unicodedata
import logging
import re
import socket
import time
import platform


def set_logger(dirname, filename):
    """Set up the log file and its format.

    dirname -- the directory where the log file will be kept.
    filename -- the log file name.
    """

    FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(dirname + "/" + filename)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.handlers[0].flush()
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.handlers[1].flush()
    

logger = logging.getLogger(__name__)
set_logger('.', 'talk2stat.log')


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="Cc")


def check_server_args(*args):
    """Check that the server invocation includes valid arguments.

    dirname -- the directory where the configuration (e.g. R.config) file is stored.
    language -- the statistical language (valid values are R, julia, matlab, or python).
    doFork -- an optional Boolean argument (default=True). If set to False, the server will still continue to run, but it will be blocking and will not return to prompt-mode until the server is stopped.
    messages -- an optional Boolean argument (default=False). If set to True, talk2stat will print the session messages to the screen.
    """

    if len(args) != 2:
        logger.critical("Usage: server(dirname, language [, doFork = True, messages = False)])")
        return False
    if not os.path.isdir(args[0]):
        logger.critical("The directory " + args[0] + " doesn't exist")
        return False
    if not args[1] in ['R' , 'julia', 'matlab', 'python']:
        logger.critical("Language has to be R, julia, matlab, or python")
        return False
    return True


def check_client_args(*args):
    """Check that the client invocation includes valid arguments.

    dirname -- the directory where the configuration (e.g. R.config) file is stored.
    language -- the statistical language (valid values are R, julia, matlab, or python).
    inputfile -- may contain either an input source file, a short command enclosed between ``` ``` to be executed directly, or 'QUIT' to stop the server.
    """

    if len(args) != 3:
        logger.critical("Usage: client(dirname, language, inputfile)")
        return False
    if not os.path.isdir(args[0]):
        logger.critical("The directory " + args[0] + " doesn't exist")
        return False
    if not args[1] in ['R' , 'julia', 'matlab', 'python']:
        logger.critical("Language has to be R, julia, matlab, or python")
        return False
    if (args[2] == 'QUIT'):
        return True
    if args[2].startswith("```"):
        return True
    if not os.path.isfile(args[2]):
        logger.critical(f'[{args[1]}] The input file {args[2]} does not exist.')
        return False
    return True


def read_config(dirname, lang):
    """Read the (language-specific) config file.

    dirname -- the directory where the configuration (e.g. R.config) file is stored.
    lang -- the statistical language (valid values are R, julia, matlab, or python).
    """

    configname = dirname + "/" + lang + ".config"
    if os.path.isfile(configname):
        config_object = ConfigParser()
        config_object.read(configname)
        return config_object["SERVERCONFIG"]
    else:
        logger.critical("Config file " + configname + " not found")
        return False


def server(*args, doFork = True, messages = False): # args = dirname, lang
    """The server function handles the bi-directional communication with the statistical package, and the communication with the client. 
    
    First argument -- the directory where the configuration (e.g. R.config) file is stored.
    Second argument -- the statistical language (valid values are R, julia, matlab, or python).
    doFork -- an optional Boolean argument (default=True). If set to False, the server will still continue to run, but it will be blocking and will not return to prompt-mode until the server is stopped.
    messages -- an optional Boolean argument (default=False). If set to True, talk2stat will print the session messages to the screen.
    """

    if platform.system() == 'Windows':
        logging.critical("On Windows 10 the talk2stat server has to run using a Linux subsystem (see documentation).")
        return False
    if not check_server_args(*args):
        return False
    dirname = args[0]
    lang = args[1]
    serverinfo = read_config(dirname, lang)
    if serverinfo == False:
        return False
    
    if doFork:
        # Fork, and exit the parent process. The child will continue to run
        pid = os.fork()
        if pid:
            sys.exit(0)
        print("pid {}".format(os.getpid()), file=open(dirname + '/serverPID' + lang + '.txt', 'w'))
    os.environ["TERM"] = "dumb" # needed for julia
    original_stdout = sys.stdout
    if lang == 'R':
        promptchar = '> '
        exe = 'R --vanilla --interactive -q'
        runfile = 'source'
    if lang == 'matlab':
        promptchar = '>>'
        exe = 'matlab -nodisplay -nosplash -nodesktop -nojvm'
        runfile = 'run'
    if lang == 'julia':
        promptchar = 'julia> '
#        exe = 'julia -q --color=no --banner=no --inline=no'
        exe = 'julia -q --color=no --banner=no'
        runfile = 'include'
    if lang == 'python':
        promptchar = '>>> '
        exe = 'python3 -iqu'
        runfile = 'exec'
    # set up a bi-directional pipe to interact with the interpreter (e.g. julia)
    child = pexpect.spawn(exe)
    fout = open(dirname + '/' + serverinfo["DEBUGFILE"],'ab')
    child.logfile = fout
    child.setecho(False)
    child.expect(promptchar.rstrip("\r\n"), timeout=60)
    if lang == 'R':
        promptchar = '>>> '
        child.sendline('options(prompt = ">>> ")')
        child.expect(promptchar.rstrip("\r\n"), timeout=60)
    logger.info(f'[{lang}] Ready')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        runbool = True
        try:
            s.bind(('127.0.0.1', int(serverinfo["PORT"])))
        except:
            logger.error(f'[{lang}:{serverinfo["PORT"]}] Another server is running using the same port?')
            return False
        s.listen()
        logger.info(f'[{lang}] Listening to port: {serverinfo["PORT"]}')
        while runbool: 
            conn, addr = s.accept()
            with conn:
                current_time = time.strftime("%Y/%M/%D %H:%M:%S", time.localtime())
                fout.write(f'\n------ {current_time} ------\n'.encode())
                if messages == True:
                    logger.info(f'[{lang}:{serverinfo["PORT"]}] Connected by: {addr}')
                buffer = []
                while True:
                    # user_input is a source file name, inline code using ``` ```, or QUIT
                    user_input = conn.recv(1024*1024).decode().rstrip()
                    if messages == True:
                        logger.info(f'[{lang}:{serverinfo["PORT"]}] User input: {user_input}')
                    if not user_input:
                        break
                    if user_input.endswith("QUIT"):
                        conn.sendall('END'.encode())
                        runbool = False
                        logger.info(f'[{lang}:{serverinfo["PORT"]}] Client termintaed.')
                        break
                    if user_input.startswith("```"):
                        child.sendline((user_input.lstrip("```").rstrip("```")))
                    else:
                        if lang == 'python':
                            child.sendline(runfile + '(open("' + user_input +'").read())')
                        else:
                            child.sendline(runfile + '("' + user_input +'")')
                    try: 
                        child.expect(promptchar.rstrip("\r\n"), timeout=int(serverinfo["PIPETIMEOUT"]))
                    except pexpect.TIMEOUT:
                        logger.warning(f'[{lang}:{serverinfo["PORT"]}] Timed out')
                        fout.write(f'  TIMED OUT {current_time} ------\n'.encode())
                        buffer.append("TIMED OUT")
                    buffer.append(remove_control_characters(str(child.before, "utf-8")))
                    buffer.append("\nEND")
                    buftmp = ''.join(buffer)
                    if messages == True:
                        logger.info(f'[{lang}:{serverinfo["PORT"]}] {buftmp}')
                    conn.sendall(buftmp.encode())
                current_time = time.strftime("%Y/%M/%D %H:%M:%S", time.localtime())
                fout.write(f'\n====== {current_time} ======\n'.encode())

    fout.close()
    child.close()
    return True


def client(*args): # args = dirname, lang, filename
    """Requests from the client are sent to the server function. They can be a file to execute in the statistical language, a short command, or QUIT to terminate the server.

    First argument -- the directory where the configuration (e.g. R.config) file is stored.
    Second argument -- the statistical language (valid values are R, julia, matlab, or python).
    Third argument -- may contain either an input source file, a short command enclosed between ``` ``` to be executed directly, or 'QUIT' to stop the server.
    """

    if not check_client_args(*args):
        return False
    dirname = args[0]
    lang = args[1]
    filename = args[2]
    serverinfo = read_config(dirname, lang)
    if serverinfo == False:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('127.0.0.1', int(serverinfo["PORT"])))
        except ConnectionRefusedError:
            logger.critical(f'[{lang}:{serverinfo["PORT"]}] Connection refused. Is server running?')
            return False
        s.sendall(filename.rstrip().encode())
        resp = ""
        while not resp.rstrip('\r\n').endswith("END"):
            resp = resp + s.recv(1024*1024).decode().rstrip('\r\n')
        print(resp.rstrip("END\n"))
    return True


__all__ = ("client", "server",)
