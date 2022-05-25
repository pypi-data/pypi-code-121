import os
import traceback
from typing import Any, Dict, List, NoReturn, Tuple
from urllib.error import HTTPError
import pip
import logging
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr
import urllib.request
import hashlib
import jsons
from dataclasses import dataclass
import subprocess
import filelock
import requests
import psutil

def get_python_exe_as_prefix():
    # Objective: we need to store state which is specific to each installation of python.  multiple installations of python can exist in the same machine: can be a conda environment, venv or the global installation.
    #    this module stores the following state for each python installation in this machine.
    #    -- write log files for infinstor_py_bootstrap
    #    -- keep the state file needed for this module: for example, to keep the timestamp of when the last check for infinstor pypi packages was done.

    # get the python executable path and use it to create your state files
    return sys.executable.replace('/','_')

def getLogger(p_logfilename: str):
    # TODO: convert to logging.config.dictConfig() later
    # create the logger for this module
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.INFO)

    # create any directory if needed.  
    dirname = os.path.dirname(p_logfilename)
    # there's a race condition – if the directory is created between the os.path.exists and the os.makedirs calls, the os.makedirs will fail with an OSError. 
    os.makedirs(dirname, exist_ok=True)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(p_logfilename)
    #fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.ERROR)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    #logger.addHandler(ch)

    return logger

def _get_infinstor_token_file_dir() -> str:
    """
    See 'Returns' below

    Returns:
        str: the directory where infinstor token file is stored.  Uses INFINSTOR_TOKEN_FILE_DIR environment variable if available..
    """
    if 'INFINSTOR_TOKEN_FILE_DIR' in os.environ:
        return os.path.join(os.environ['INFINSTOR_TOKEN_FILE_DIR'])
    else:
        return os.path.join(os.path.expanduser("~"), ".infinstor")
    
# TODO: On one hand, log must not be per user;  it must be per python environment (conda, virtualenv, global etc) since the packages are installed in each python environment.. 
#       On the other hand, we have ~/.infinstor/token and ~/.aws/credentials, which is per user.  All python envs in the same OS userid share these files, so in reality only one active python env per user is usually used 
#       (if multiple active envs are used, they need to use the same staging environment so that the same token value holds; but each env will attempt to update the token file with its own login results, so not sure what the reuslt will be)
#
# copy of below code also exists in infinstor-jupyterlab/clientlib/infinstor/mlflow_run.py
file_prefix = os.path.join( _get_infinstor_token_file_dir() , get_python_exe_as_prefix())
logfile_name = file_prefix + '_' + __name__ + '.log.txt'
logger = getLogger(logfile_name)

@dataclass
class GetVersionResponse:
    cognitoCliClientId:str = ""
    cognitoAppClientId:str = ""
    mlflowDnsName: str = ""
    mlflowuiDnsName: str = ""
    mlflowstaticDnsName: str = ""
    apiDnsName: str = ""
    serviceDnsName: str = ""
    region:str     = ""
    service:str = None
    """note that 'service' is not part of the response from https://mlflow.infinstor.com/api/2.0/mlflow/infinstor/get_version.  It is populated by the method below"""

# cache fetched value
_get_version_resp:GetVersionResponse = None
    
def _bootstrap_config_values_from_mlflow_rest_if_needed() -> GetVersionResponse:
    """ makes a REST call to https://mlflow.infinstor.com/api/2.0/mlflow/infinstor/get_version and constructs an instance of GetVersionResponse using the response

    Raises:
        Exception: if MLFLOW_TRACKING_URI is not set, raises an exception

    Returns:
        GetVersionResponse: the response from https://mlflow.infinstor.com/api/2.0/mlflow/infinstor/get_version REST call
    """
    ##########
    #  TODO: a copy exists in 
    #  infinstor-mlflow/plugin/infinstor_mlflow_plugin/login.py 
    #  infinstor-mlflow/processors/singlevm/scripts/rclocal.py
    #  infinstor-jupyterlab/server-extension/jupyterlab_infinstor/__init__.py
    #  infinstor-jupyterlab/server-extension/jupyterlab_infinstor/cognito_utils.py
    #  infinstor-jupyterlab/clientlib/infinstor/bootstrap.py
    #  infinstor-jupyterlab/infinstor_py_bootstrap_project/infinstor_py_bootstrap/infinstor_py_bootstrap.py
    #  Need to see how to share code between two pypi packages to eliminate this duplication
    #  when refactoring this code, also refactor the copies
    ############
    
    global _get_version_resp
    if _get_version_resp: return _get_version_resp
    
    # note that this code (server-extension code) runs in the jupyterlab server, where MLFLOW_TRACKING_URI was not set earlier.  Now it needs to be set correctly to the mlflow api hostname: mlflow.infinstor.com.  Note that 'mlflow' in the hostname is not hardcoded.. it can be a different subdomain name
    #
    muri = os.getenv('MLFLOW_TRACKING_URI')
    pmuri = urllib.parse.urlparse(muri)
    if (pmuri.scheme.lower() != 'infinstor'):
        raise Exception(f"environment variable MLFLOW_TRACKING_URI={muri} has an invalid value or the url scheme != infinstor.  Set the environment variable correctly and restart the process")
    # extract 'infinstor.com' from 'mlflow.infinstor.com'
    cognito_domain = pmuri.hostname[pmuri.hostname.index('.')+1:]
    url = 'https://' + pmuri.hostname + '/api/2.0/mlflow/infinstor/get_version'
    
    headers = { 'Authorization': 'None' }
    try:
        response:requests.Response = requests.get(url, headers=headers)
        logger.info(f"response for {url}={response}; response.text={response.text}")
        response.raise_for_status()
        resp = response.json()
        
        get_version_resp:GetVersionResponse = jsons.load(resp, GetVersionResponse)
        get_version_resp.service = cognito_domain
        return get_version_resp
    except HTTPError as http_err:
        logger.error(f"Caught Exception: {http_err}:",exc_info=http_err )
        return None
    except Exception as err:
        logger.error(f"Caught Exception: {err}",exc_info=err )
        return None

import urllib.parse

def _isPipInstallCmd(cmd_line:List[str]) -> bool:
    # linux: sys.executable=/home/isstage17/miniconda3/envs/infinstor/bin/python ; sys.argv=['/home/isstage17/miniconda3/envs/infinstor/bin/pip', 'install', '--upgrade', '--index-url', 'http://cvat.infinstor.com:9876/simple', '--extra-index-url', 'https://www.pypi.org/simple', '--trusted-host', 'cvat.infinstor.com:9876', '--trusted-host', 'www.pypi.org', '--retries', '2', '--timeout', '3', 'infinstor==2.0.24', 'jupyterlab-infinstor==2.0.12', 'infinstor-mlflow-plugin==2.0.28']
    # windows: sys.executable=C:\Users\Raj\.conda\envs\infinstor\python.exe ; sys.argv=['C:\\Users\\Raj\\.conda\\envs\\infinstor\\Scripts\\pip-script.py', 'install', '--upgrade', '--index-url', 'https://www.pypi.org/simple', '--extra-index-url', 'http://pip.infinstor.com', '--trusted-host', 'www.pypi.org', '--trusted-host', 'pip.infinstor.com', '--retries', '2', '--timeout', '3', 'infinstor-py-bootstrap==1.0.3', 'infinstor==2.0.33', 'jupyterlab-infinstor==2.0.15', 'infinstor-mlflow-plugin==2.0.35']
    is_pip_install_cmd:bool = ( 
                               any(s.endswith("pip") for s in cmd_line) or 
                               any(s.endswith("pip3") for s in cmd_line) or 
                               any(s.endswith("pip-script.py") for s in cmd_line) 
                              ) and any('install' == s for s in cmd_line)
    logger.info(f"_isPipInstallCmd={is_pip_install_cmd}; cmd_line={cmd_line}")
    return is_pip_install_cmd

def _isDescendentOfPipInstall() -> bool:
    """
    if this process is a descendent of a 'pip install' command, do not try an auto update since we want to avoid infinite recursion: we do not do an auto update if it is a 'pip install' as auto update launches a 'pip install'..

    _extended_summary_

    Returns:
        bool: returns True if descendent, False otherwise
    """
    # get current process
    curr_proc:psutil.Process = psutil.Process()
    with curr_proc.oneshot():
        ancestors:List[psutil.Process] = curr_proc.parents()
        for ancestor in ancestors:
            if _isPipInstallCmd(ancestor.cmdline()): 
                logger.info(f"detected an ancestor pip install command: ancestor.pid={ancestor.pid}; ancestor.exe={ancestor.exe()}; ancestor.cmdline={ancestor.cmdline()}")
                return True
            #print(ancestor.cmdline())
    
    return False

def _pip_install_or_upgrade(pip_index_url:str, pip_extra_index_urls:list, packages_with_ver:list, logger:logging.Logger) -> bool:
    """runs 'pip install --upgrade' for the specified arguments

    Args:
        pip_index_url (str): passed to pip's --index-url
        pip_extra_index_urls (list): passed to pip's --extra-index-url
        packages_with_ver (list): list of packages to be installed or upgraded
        logger (logging.Logger): logger to use for logging

    Returns:
        bool: True if pip returns success; False if pip fails
    """
    # if "index url" is not specified, use the default.
    if not pip_index_url:  pip_index_url = 'https://www.pypi.org/simple'
    
    # pip_index_url can be similar to https://www.pypi.org/simple; we need to extract just www.pypi.org from this URL to pass as an argument to --trusted-host.  If not done, pip reports an error similar to 'ValueError: Invalid IPv6 URL'..
    #
    # Parse a URL into 6 components:
    # <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    # Return a 6-tuple: (scheme, netloc, path, params, query, fragment). Note that we don't break the components up in smaller bits (e.g. netloc is a single string) and we don't expand % escapes.
    parsed_url:urllib.parse.ParseResult = urllib.parse.urlparse(pip_index_url)
    pip_trusted_host_args:list=['--trusted-host', parsed_url.netloc]
    
    # if "extra index URLs" are not specified, use default empty list.
    pip_extra_index_url_args:list=[]
    # if "extra index URLs" are specified
    if pip_extra_index_urls:    
        for pip_extra_index_url in pip_extra_index_urls:
            pip_extra_index_url_args.append('--extra-index-url')
            pip_extra_index_url_args.append(pip_extra_index_url)
            
            # extra_index_url can be similar to https://www.pypi.org/simple; we need to extract just www.pypi.org from this URL to pass as an argument to --trusted-host.  If not done, pip reports an error similar to 'ValueError: Invalid IPv6 URL'..
            parsed_url:urllib.parse.ParseResult = urllib.parse.urlparse(pip_extra_index_url)
            pip_trusted_host_args.append('--trusted-host')
            pip_trusted_host_args.append(parsed_url.netloc)            
    
    # http PyPI index: WARNING: The repository located at mypypi.com.url is not a trusted or secure host and is being ignored. If this repository is available via HTTPS we recommend you use HTTPS instead, otherwise you may silence this warning and allow it anyway with '--trusted-host mypypi.com.url'
    # 
    # retricts retries to 2 and timeout to 3 seconds, so that we don't spend too much time on python interpreter startup, when the package index is not reachable
    # popen won't  work: see further below: use popen so that output from pip does not go to stdout (which confuses any tool like vscode which parses interpreter startup output)
    pip_args = ['install', '--upgrade', '--index-url', pip_index_url, *pip_extra_index_url_args, *pip_trusted_host_args,  '--retries', '2', '--timeout', '3', *packages_with_ver]
    logger.info(f"pip_args={pip_args}")
    
    # option 1: use pip module and call pip.main().  This is not very reliable.
    #
    # below logger() call fails when we use open('tmp/output.txt', 'w+b'): could it be due to the redirect_stdout() call below closing the file handle 'fh'???
    #    File "/home/raja/miniconda3/envs/infinstor/lib/python3.8/site-packages/pip/_internal/utils/logging.py", line 215, in should_color
    #        if hasattr(real_stream, "isatty") and real_stream.isatty():
    #    File "/home/raja/miniconda3/envs/infinstor/lib/python3.8/tempfile.py", line 474, in func_wrapper
    #        return func(*args, **kwargs)
    #    ValueError: I/O operation on closed file    
    # logger.info("running pip ")
    #
    # Note: 'pip.main()' call below will only write log output to stdout.  does not take a 'file handle' to 'pip.main()' call to write log output to a file
    # Note: it seems pip.main() code below uses the logging module.. it seems like it uses logging.basicConfig() and configures 'logging' to use stdout and stderr pointing to the temporary file used below.
    #     But when the 'with' statement below finishes, the temporary file is closed and removed but logging still holds the stdout that points to the closed temporary file.. as a result, 
    #     code that relies on logging.basicConfig() (like clientlib), fails with the error above: "ValueError: I/O operation on closed file", since any calls to the logging that uses basicConfig uses this closed file.
    # 
    # 
    # with tempfile.NamedTemporaryFile('w+') as tf, redirect_stdout(tf), redirect_stderr(tf):
        # if hasattr(pip, 'main'):
        #     pip.main(pip_args)
        # else:
        #     # TODO: handle if pip install fails
        #     pip._internal.main(pip_args)
        
        # rewind the tempfile and read it.. log the contents
        # tf.seek(0)
        # logger.info("pip output = \n%s", tf.read())

    # option 2: run pip as a subprocess.  this is more reliable
    try:
       pip_args_with_pip_prepended:list = ['pip']
       pip_args_with_pip_prepended.extend(pip_args)
       process:subprocess.Popen = subprocess.Popen(pip_args_with_pip_prepended, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL, close_fds=True)
       for line in process.stdout:
            lined = line.decode('utf-8').rstrip()
            logger.info(lined)
       retcode:int = process.wait()       
       # completed_process = subprocess.run(pip_args_with_pip_prepended, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) #, timeout=30)
       logger.info(f"return code from pip install = {process.returncode}; ran pip cmd={pip_args_with_pip_prepended}")
       # logger.info("output of pip command"); logger.info(completed_process.stdout.decode("utf-8")); logger.info("end of output of pip command"); 
       return True if process.returncode == 0 else False
    except:
       logger.error(f"_pip_install_or_upgrade(): Caught an exception: {''.join(traceback.format_exception(*sys.exc_info()))}")
    
    # return an error
    return False

# Read the specified environment value and return its value.  also accepts a default value
def readEnvVar(varName, defaultValue):
    varValue=os.environ.get(varName)
    # if env var not defined, use default
    if not varValue: varValue = defaultValue
    return varValue

def serialize_instance(obj) -> dict:
    d = { '__classname__' : type(obj).__name__ }
    d.update(vars(obj))
    return d

def deserialize_instance(d) :
    clsname = d.pop('__classname__', None)
    if not clsname: 
        logger.error("__classname__ not found in %s", d)
        return d
    
    clstype = globals().get(clsname)
    #print(f"clstype={clstype}")
    if not clstype: 
        logger.error("Not able to locate the class instance for __classname__ = %s ", clsname)
        return d

    obj = clstype.__new__(clstype)   # Make instance without calling __init__
    for key, value in d.items():
        setattr(obj, key, value)
    return obj

# {
#     "__classname__": "InfinstorServiceVersion",
#     "service_version": "1.1.1",
#     "pip_index_url": "https://www.pypi.org/simple",
#     "pip_extra_urls": [
#         "https://pip.infinstor.com"
#     ],
#     "infinstor_web_version": "2.2.2",
#     "infinstor_lambda_version": "3.3.3",
#     "infinstor_mlflow_lambda_version": "4.4.4",
#     "client_python_package_versions": {
#         "infinstor": "infinstor>=1.2,<2",
#         "jupyterlab-infinstor": "jupyterlab-infinstor>=0.7,<1"
#     },
#     "client_npm_pack_versions": {
#         "jupyterlab_infinstor": "7.7.7"
#     }
# }
@dataclass
class InfinstorServiceVersion(jsons.JsonSerializable):
    #service_name:str                            # service_name like isstage2

    client_python_package_versions:Dict[str,str]         # version for python packages: infinstor (clientlib), jupyterlab-infinstor (server-extension) and infinstor-mlflow-plugin (infinstor-mlflow/plugin)
    client_npm_package_versions:Dict[str,str]            # version for npm package: jupyterlab-infinstor (browser_component)
    
    service_version:str = None                         # service version
    
    infinstor_web_version:str = None                   # infinstor-web version
    infinstor_lambda_version:str = None                # infinstor/lambda version
    infinstor_mlflow_lambda_version:str = None         # infinstor-mlflow/server/lambda version
    
    pip_index_url:str = 'https://www.pypi.org/simple'                           # pip index url for pypi repository
    pip_extra_index_urls:List[str] = ('https://pip.infinstor.com')              # pip extra index urls for additional pypi compliant repositories
    
    # "optimized" == rely on hash of infinstor_service_version.json to determine if auto update must be done or not.  faster than "normal" but will only work for '==' version specifiers (no ranges)
    #      Do not use this when version ranges for python packages are specifed in the json
    #      because the hash may not have changed (and no auto update will be attempted) but in reality an auto-update may be needed (say a version range is used in the version specifier in json and a newer version
    #      of a python package is uploaded to pypi that matches this version range)
    # "disabled"  == disable auto update..
    # "normal"  == the above hash based check is disabled.  And pip is used to determine if an update is needed..  slower than "optimized" but will work for all scenarios.
    auto_update_strategy:str = "optimized"
    
# TODO: DUPLICATED: have copies in other .py files. refactor later
# {
#     "rclocal_shutdowndelay": 115,
#     "clientlib_verbose": false,
# }
@dataclass
class InfinstorConfig(jsons.JsonSerializable):
    rclocal_shutdowndelay:int = 15                         # delay in minutes
    clientlib_verbose:bool = False                         
    server_extension_cognito_utils_verbose:bool = False

# {
#     "infin_service_ver_json_hash":"abcdef"
# }
@dataclass
class InfinstorState(jsons.JsonSerializable):
    infin_service_ver_json_hash:str = None

def readTokenFile() -> dict:
    """
    get service name from ~/.infinstor/token file
    
    ```    
    Token=eyJraWQiOiJBbzl....    
    RefreshToken=eyJjdHki....    
    ClientId=18mud50v909ttblt1qri88vru8    
    TokenTimeEpochSeconds=1618919185    
    Service=isstage2.com    
    ```
    """
    myvars = {}
    try:
        with open( os.path.join(_get_infinstor_token_file_dir(), "token"), 'r' ) as myfile:
            for line in myfile:                
                line = line.rstrip()  #strip last character if it is a newline
                logger.info(f"line in tokenFile: {line}")
                name, var = line.partition("=")[::2]     # 2 == step size
                myvars[name.strip()] = var
    except Exception as e:
        logger.error("Caught exception: ", exc_info=e)
    return myvars
      
def downloadJsonUrlAndDeser(url:str, cls) -> Tuple[bytes,Any]:
    """
    downloads the json from specified 'url' and deserializes it to an instance of the specified 'cls'

    [extended_summary]

    Args:
        url (str): URL for the json to be downloaded

    Returns:
        Tuple[bytes,Any]: on Success, returns the Tuple ( json_response_as_string_from_url , deserialized json as an instance of specified 'cls' ); None on failure
    """
    try:
        with urllib.request.urlopen(url, timeout=10, ) as f:
            urlcontents:str = f.read()   #read the contents of the url            
            return (urlcontents, jsons.loads(urlcontents, cls))
    except Exception as e:
        logger.error(f"Caught exception for url={url}: ", exc_info=e)

    return (None,None)

# TODO: DUPLICATED: have copies in other .py files. refactor later    
def readJsonFileAndDeser(filename:str, cls, use_lock_file=False) -> Tuple[str,Any]:
    """
    Reads the specified json file and deserializes it into the 'cls' that is specified.  Returns the read json(as a string) and the deserialized instance
    """
    
    if (use_lock_file):
        # protect with a filelock: multiple processes can read and write to a json at the same time (multiple python processes launched concurrently, like ipython kernel startups when connecting to a notebook server).
        lock:filelock.FileLock = filelock.FileLock(filename + ".lock", timeout=2 )
        
        with lock:    # lock is acquired here
            return readJsonFileAndDeserUnlocked(filename, cls)
        # lock is released here; do not delete the lock file; see UnixFileLock source code for details
    
    return readJsonFileAndDeserUnlocked(filename, cls)
    
def readJsonFileAndDeserUnlocked(filename:str, cls) -> Tuple[str,Any]:
    """
    Reads the specified json file and deserializes it into the 'cls' that is specified.  Returns the read json(as a string) and the deserialized instance
    """
    # use empty json as the default
    filecontents = '{}'
    try:
        if os.path.isfile(filename):   # check for file existence before attempting to open() below since open() raises an exception if file not found
            with open(filename, "r") as f:
                filecontents:str = f.read()   #read the contents of the url            
    except Exception as e:
        logger.error("Caught exception: ", exc_info=e)
        
    return (filecontents, jsons.loads(filecontents, cls))

def serializeObjToJsonFile(obj: Any, filename:str, use_lock_file=False) -> str:
    """ 'obj' is the instance to be serialized to 'filename' as json.. returns the serialized json """
    if (use_lock_file):
        # protect with a filelock: multiple processes can read and write to a json at the same time (multiple python processes launched concurrently, like ipython kernel startups when connecting to a notebook server).
        lock:filelock.FileLock = filelock.FileLock(filename + ".lock", timeout=2 )
        
        with lock:    # lock is acquired here
            return serializeObjToJsonFileUnlocked(obj, filename)
        # lock is released here; do not delete the lock file; see UnixFileLock source code for details
    
    return serializeObjToJsonFileUnlocked(obj, filename)
    
def serializeObjToJsonFileUnlocked(obj: Any, filename:str) -> str:
    """ 'obj' is the instance to be serialized to 'filename' as json.. returns the serialized json """
    try:
        with open(filename, "w") as f:
            dumped:str = jsons.dumps(obj)
            f.write(dumped)
            return dumped
    except Exception as e:
        logger.error("Caught exception: ", exc_info=e)
        
    return None
    
def getMd5Hash(input_json_bytes:bytes) -> str:
    #input_json_bytes = inputstr.encode('utf-8')
    return hashlib.md5(input_json_bytes).hexdigest()

def isSingleVMTransformRunPythonProcess() -> bool:
    """
    Detect if the current python process is running a transform in a single VM.  We only want to perform auto update of python packages if the python process is running a transform.
    """
    # root      4057     1  0 Mar12 ?        00:00:00 /bin/bash /etc/rc.d/rc.local start
    # root      4226  4057  0 Mar12 ?        00:00:00  \_ /usr/bin/python3 /opt/infinstor/bin/real-rclocal.py no_gpu
    # root      4227  4226  0 Mar12 ?        00:00:00      \_ [curl] <defunct>
    # root     19214  4226  0 Mar12 ?        00:00:00      \_ /usr/bin/sudo -u ec2-user MLFLOW_TRACKING_URI=infinstor://infinstor.com/ GIT_PYTHON_REFRESH=quiet NVIDIA_VISIBLE_DEVICES=all COGNITO_USERNAME=prachi-multilex MLFLOW_CONDA_HOME=/home/ec2-user/anaconda3 -s /home/ec2-user/anaconda3/bin/mlflow run -A publish-all -A name=5-c2ce67687c2f412bb2d7527e6408ddd0 /tmp/tmpcozpy4j3 --run-id 5-c2ce67687c2f412bb2d7527e6408ddd0 -P xformname=scraper_trans -P input_data_spec={"type": "infinsnap", "bucketname": "multilex-s3-bucket-prachi", "prefix": "", "time_spec": "tm20210312164829"} -P service=infinstor.com
    # ec2-user 19216 19214  0 Mar12 ?        00:00:01      |   \_ /home/ec2-user/anaconda3/bin/python /home/ec2-user/anaconda3/bin/mlflow run -A publish-all -A name=5-c2ce67687c2f412bb2d7527e6408ddd0 /tmp/tmpcozpy4j3 --run-id 5-c2ce67687c2f412bb2d7527e6408ddd0 -P xformname=scraper_trans -P input_data_spec={"type": "infinsnap", "bucketname": "multilex-s3-bucket-prachi", "prefix": "", "time_spec": "tm20210312164829"} -P service=infinstor.com
    # ec2-user 21056 19216  0 Mar12 ?        00:00:00      |       \_ bash -c source /home/ec2-user/anaconda3/bin/../etc/profile.d/conda.sh && conda activate mlflow-b93f56de2f92442c1c31e5be67923484a33b2534 1>&2 && python -c 'from infinstor import mlflow_run; mlflow_run.main()'                --input_data_spec='{"type": "infinsnap", "bucketname": "multilex-s3-bucket-prachi", "prefix": "", "time_spec": "tm20210312164829"}' --service=infinstor.com                --xformname=scraper_trans
    # ec2-user 21067 21056  0 Mar12 ?        00:00:17      |           \_ python -c from infinstor import mlflow_run; mlflow_run.main() --input_data_spec={"type": "infinsnap", "bucketname": "multilex-s3-bucket-prachi", "prefix": "", "time_spec": "tm20210312164829"} --service=infinstor.com --xformname=scraper_trans
    # root     19215  4226  0 Mar12 ?        00:00:29      \_ /usr/bin/python3 /opt/infinstor/bin/real-rclocal.py no_gpu
    
    # python -c "import sys; print(sys.argv)" --input_data_spec='{"type": \"infinsnap", "bucketname": "multilex-s3-bucket-prachi", "prefix": "", "time_spec": "tm20210312164829"}' --service=infinstor.com --xformname=scraper_trans
    # ['-c', '--input_data_spec={"type": \\"infinsnap", "bucketname": "multilex-s3-bucket-prachi", "prefix": "", "time_spec": "tm20210312164829"}', '--service=infinstor.com', '--xformname=scraper_trans']
    transformrun='-c' in sys.argv and any('--input_data_spec' in s for s in sys.argv) and any('--service' in s for s in sys.argv) and  any('--xformname' in s for s in sys.argv)
    logger.info(f"transformrun detected={transformrun}")
    return transformrun

def isJupyterlabPythonProcess() -> bool:
    # /home/dev/miniconda3/envs/infinstor/bin/python /home/dev/miniconda3/envs/infinstor/bin/jupyter-lab --log-level INFO --no-browser --ip=0.0.0.0 --port 9002
    # sys.executable=/home/dev/miniconda3/envs/infinstor/bin/python ; sys.argv=['/home/dev/miniconda3/envs/infinstor/bin/jupyter-lab', '--log-level', 'INFO', '--no-browser', '--ip=0.0.0.0', '--port', '9002']
    #
    # sys.executable=/home/dev/miniconda3/envs/infinstor/bin/python ; sys.argv=['/home/dev/miniconda3/envs/infinstor/bin/jupyter', 'lab', '--log-level', 'INFO', '--no-browser', '--ip=0.0.0.0', '--port', '9002']
    # sys.executable=/home/dev/miniconda3/envs/infinstor/bin/python ; sys.argv=['/home/dev/miniconda3/envs/infinstor/bin/jupyter-lab', '--log-level', 'INFO', '--no-browser', '--ip=0.0.0.0', '--port', '9002']
    jupyterlab = any('bin/jupyter-lab' in s for s in sys.argv)
    logger.info(f"jupyterlab detected={jupyterlab}")
    return jupyterlab

def isJupyterlabIPythonKernelPythonProcess() -> bool:
    # sys.executable=/home/dev/miniconda3/envs/infinstor/bin/python ; sys.argv=['-m', '-f', '/home/dev/.local/share/jupyter/runtime/kernel-65658fa4-7b42-4a55-8b0d-4948d72c29c7.json']
    # /home/dev/miniconda3/envs/infinstor/bin/python -m ipykernel_launcher -f /home/dev/.local/share/jupyter/runtime/kernel-65658fa4-7b42-4a55-8b0d-4948d72c29c7.json
    #
    # sys.executable=/home/dev/miniconda3/envs/infinstor/bin/python ; sys.argv=['-m', '-f', '/home/dev/.local/share/jupyter/runtime/kernel-749dcbfa-2de6-4f59-927a-7fb3afc20797.json']
    ipythonkernel = '-m' in sys.argv and '-f' in sys.argv and any('runtime/kernel' in s for s in sys.argv)
    logger.info(f"ipythonkernel detected={ipythonkernel}")
    return ipythonkernel
    
def main():
    try:
        # this is the first line of the invocation of this hook; added a newline prior to printing so that log file is easier to read: each run is separated by an empty line
        logger.info(''); logger.info('')
        logger.info('sys.executable=%s ; sys.argv=%s', sys.executable, sys.argv)
        
        mlflow_tracking_uri =os.environ.get("MLFLOW_TRACKING_URI")
        if not (mlflow_tracking_uri and mlflow_tracking_uri.startswith("infinstor:")):
            logger.info(f"Not performing auto update since python process is not related to infinstor platform: MLFLOW_TRACKING_URI={mlflow_tracking_uri}\n\n")
            return
        
        # sys.executable=/home/isstage17/miniconda3/envs/infinstor/bin/python ; sys.argv=['/home/isstage17/miniconda3/envs/infinstor/bin/pip', 'install', '--upgrade', '--index-url', 'http://cvat.infinstor.com:9876/simple', '--extra-index-url', 'https://www.pypi.org/simple', '--trusted-host', 'cvat.infinstor.com:9876', '--trusted-host', 'www.pypi.org', '--retries', '2', '--timeout', '3', 'infinstor==2.0.24', 'jupyterlab-infinstor==2.0.12', 'infinstor-mlflow-plugin==2.0.28']
        # if this hook is invoked for 'pip install' command (see command above), then stop this hook from executing further.  
        # when a 'pip' subprocess is started, this 'pth' hook will be called, which will then attempt to start another 'pip' subprocess.  this will lead to infinite recursion 
        #    (since first 'pip' subprocess  --> starts the python interpreter --> 'site-packages/infinstor_py_bootstrap.pth' called --> launches another pip subprocess --> cycle repeats).
        #    Eventually the VM runs out of memory due to too many processes.
        if _isPipInstallCmd(sys.argv) or _isDescendentOfPipInstall():
            logger.info(f"Not performing auto update since python process is 'pip install' or a descendent of 'pip install': avoid infinite recursion.\n\n")
            return

        get_version_resp:GetVersionResponse = _bootstrap_config_values_from_mlflow_rest_if_needed()
        
        # download https://<service_name>/assets/infinstor_service_version.json
        infin_service_ver_json_url = f"https://{get_version_resp.serviceDnsName}.{get_version_resp.service}/infinstor_service_version.json"
        jsonbytes:bytes; infin_service_ver:InfinstorServiceVersion; (jsonbytes, infin_service_ver) = downloadJsonUrlAndDeser(infin_service_ver_json_url, InfinstorServiceVersion)
        # if file can't be downloaded or not valid json, then abort auto update
        if not infin_service_ver: 
            logger.error("Aborting auto update since %s cannot be downloaded or is not a valid json", infin_service_ver_json_url)
            return
        logger.info(f"infin_service_ver={infin_service_ver};  json={jsonbytes}")
        
        # even if infinstor_service_version.json hasn't been updated, we still will try a 'pip install' since version ranges can be used in infinstor_service_version.json 
        #    and new versions of python packages could have been uploaded to pypi.org that matches the version range specified.
        
        if ( infin_service_ver.auto_update_strategy.lower() == "normal" or infin_service_ver.auto_update_strategy.lower() == "optimized" ):
            # check if hash of infinstor_service_version.json has changed or not..
            if ( infin_service_ver.auto_update_strategy.lower() == "optimized" ):
                (has_hash_changed, infin_state, new_hash) = has_changed_infinstor_service_version_json(jsonbytes, infin_service_ver_json_url)
                # if hash has not changed, return.  Note that if newer versions of packages have been uploaded to pypi, an auto update will not happen, since the hash hasn't changed.
                if not has_hash_changed: 
                    logger.info(f"Not doing auto update since {infin_service_ver_json_url} has not changed: md5 hash is the same: old={infin_state.infin_service_ver_json_hash}, new={new_hash}")
                    return
                
                logger.info(f"Performing an auto update since {infin_service_ver_json_url} has changed: md5 hash: old={infin_state.infin_service_ver_json_hash}, new={new_hash}")

                
            # for each python package in infinstor_service_version.json, update using pip
            #
            # note that in single VM run, the conda environment is created by 'mlflow run' command, based on the conda.yaml specified by the MLproject..
            #    If we 'auto update' packages in this conda environment created by mlflow, in the next invocation of "mlflor run" for the same conda.yaml, 'mlflow run' will still 
            #    reuse this conda environment (even if we have modified the python packages in this conda environment such that the conda env is out of sync with conda.yaml).  
            #    this reuse is due to the use of a 'hash' of conda.yaml by mlflow.utils.conda.py code (see below) to create the conda environment name: the hash is included in the 
            #    created env name (like mlflow-xxxxxxxxxxxxx) so that there is 1-1 mapping between the conda.yaml contents and its conda environment name.
            #    if 'mlflow run' were to compare the packages installed in the conda env with the conda.yaml, it will find discrepencies for the 'auto updated' packages, but it doesn't do this..
            #
            # code from mlflow below:
            # def mlflow.utils.conda.py::get_or_create_conda_env(conda_env_path, env_id=None):
            #     """
            #     Given a `Project`, creates a conda environment containing the project's dependencies if such a
            #     conda environment doesn't already exist. Returns the name of the conda environment.
            #     :param conda_env_path: Path to a conda yaml file.
            #     :param env_id: Optional string that is added to the contents of the yaml file before
            #                 calculating the hash. It can be used to distinguish environments that have the
            #                 same conda dependencies but are supposed to be different based on the context.
            #                 For example, when serving the model we may install additional dependencies to the
            #                 environment after the environment has been activated.
            #     """            
            pip_success:bool = _pip_install_or_upgrade(infin_service_ver.pip_index_url, infin_service_ver.pip_extra_index_urls, infin_service_ver.client_python_package_versions.values(), logger)
            
            if (pip_success and infin_service_ver.auto_update_strategy.lower() == "optimized" ):
                #only if the auto update is successful, update the hash in state.json..                 
                update_infinstor_service_version_json(jsonbytes, infin_state)
        elif infin_service_ver.auto_update_strategy.lower() == "disabled":
            logger.info(f"Not performing auto update since auto update is disabled in {infin_service_ver_json_url}")
        else:
            logger.error(f"Unsupported value for auto_update_strategy={infin_service_ver.auto_update_strategy} in {infin_service_ver_json_url}")
    except Exception as e:
        logger.error("Exception caught: ", exc_info=e)

def _get_state_json_filename() -> str:
    """ see return value below

    Returns:
        str: full pathname to state.json for this python environment.  Each python environment (conda global or conda or docker) has its own state.json.  the full filename pattern is ~/.infinstor/<python_binary_full_path_with_slash_replaced_with_underscores>_state.json
    """
    return os.path.join(_get_infinstor_token_file_dir(), get_python_exe_as_prefix() + "_state.json")
    
def has_changed_infinstor_service_version_json(jsonbytes:bytes, infin_service_ver_json_url) -> Tuple[bool, InfinstorState, str] :
    "returns if the hash has changed, the state.json instance (with the old hash) and the new hash"
    infin_service_ver_md5 = getMd5Hash(jsonbytes)
        
    state_json_fname = _get_state_json_filename()
    # get the last seen infinstor_service_version.json's md5 hash; ; use lock since multiple processes can access state.json at the same time
    infin_state:InfinstorState; jsonstr:str; jsonstr, infin_state = readJsonFileAndDeser(state_json_fname, InfinstorState, use_lock_file=True)
    # if state.json file is found and doesn't have md5 hash
    if infin_state and not getattr(infin_state, "infin_service_ver_json_hash", None): 
        # initialize to an empty hash string
        infin_state.infin_service_ver_json_hash = ''
    
    # if the infin_service_ver json hasn't changed, then abort auto update
    if infin_service_ver_md5 == infin_state.infin_service_ver_json_hash: 
        return (False, infin_state, infin_service_ver_md5)
    
    return (True, infin_state, infin_service_ver_md5)

def update_infinstor_service_version_json(jsonbytes:bytes, infin_state:InfinstorState):
    old_hash:str = None
    infin_service_ver_md5 = getMd5Hash(jsonbytes)
    
    # the infinstor_service_version.json file has been updated.  So save the new hash in state.json    
    # if state.json exists, update the hash in the json
    if infin_state:
        old_hash = infin_state.infin_service_ver_json_hash
        infin_state.infin_service_ver_json_hash = infin_service_ver_md5
    else:   # state.json doesn't exist, so create it..
        old_hash = None
        infin_state = InfinstorState(infin_service_ver_json_hash=infin_service_ver_md5)
    
    state_json_fname =  _get_state_json_filename()
    logger.info(f"persisting/updating {state_json_fname}: old hash={old_hash} to new hash={infin_service_ver_md5}")
    # persist state.json; use lock since multiple processes can access state.json at the same time
    serializeObjToJsonFile(infin_state,state_json_fname, use_lock_file=True)

if __name__ == '__main__':
    main()
