import logging
import os
import sys
import uuid
import re
from datetime import datetime
import subprocess
from dateutil.relativedelta import relativedelta
from sumoappclient.common.utils import get_normalized_path
from sumoappclient.common.logger import get_logger
import boto3

DATE_FORMAT = "%Y-%m-%d-%H-%M-%S"
FILE_PREFIX = "apptests"
LOG_FILES_DELETION_DAYS = 7
ALL_APPS_FILENAME = "full_app_list.txt"
PUSH_SCRIPT_FILENAME = "push_new_sumo_app.bash"
EXCLUDED_APP_PREFIXES = ("PCI/PCIv2", "SecurityApp", "//")
EXCLUDED_MODULE_LOGGING = ("requests", "urllib3")
EXCLUDED_APPS_WITHOUT_SC_PARAMS = (
    "Global Intelligence for Amazon GuardDuty",
    "Data Volume",
    "Data Volume (Legacy)",
    "Audit",
    "Artifactory",
    "Enterprise Audit - Collector & Data Forwarding Management",
    "Enterprise Audit - Content Management",
    "Enterprise Audit - Security Management",
    "Enterprise Audit - User & Role Management",
    "Global Intelligence for CloudTrail DevOps",
    "Global Intelligence for AWS CloudTrail SecOps",
    "Amazon EKS - Control Plane",
    "Kubernetes - Control Plane < 1.16",
    "Kubernetes - Control Plane >= 1.16",
    "PCI Compliance"
)


def get_content_directory_from_wd():
    work_dir = os.getcwd()
    work_dir = work_dir.split("content")[0]
    work_dir = os.path.join(work_dir, "content")
    return work_dir


class ENVIRONMENT:
    CONTENT_DIR = os.getenv("CONTENT_DIR", get_content_directory_from_wd())
    SUMO_APP_UTILS_MODE = os.getenv("SUMO_APP_UTILS_MODE", "PARTNER")
    SUMO_DEPLOYMENT = os.getenv("SUMO_DEPLOYMENT")


def get_content_dirpath():
    content_dirpath = ENVIRONMENT.CONTENT_DIR
    return get_normalized_path(content_dirpath)


def get_file_data(filepath):
    data = None
    with open(filepath) as fp:
        data = fp.read()
    return data


class USER(object):
    '''
        Do not trust these parameters anyone can modify them so use it for small things like creating folder

    '''

    @property
    def is_partner(self):
        return ENVIRONMENT.SUMO_APP_UTILS_MODE == "PARTNER"


USER = USER()


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def get_test_log_dir():
    log_dir = os.path.join(os.getcwd(), "testlogs")
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    return log_dir


def get_test_log_file_name():

    BUILD_NUMBER = os.environ.get("BUILD_NUMBER", "UNKNOWN")
    ID = uuid.uuid4().hex[:8]
    current_date = datetime.now().strftime(DATE_FORMAT)
    FILENAME = "_".join([FILE_PREFIX, current_date,
                         BUILD_NUMBER, ID]) + '.log'
    LOGFILE = os.path.join(get_test_log_dir(), FILENAME)
    return LOGFILE


def do_cleanup(log):

    LOG_DIR = get_test_log_dir()
    last_week_date = datetime.now() - relativedelta(days=LOG_FILES_DELETION_DAYS)
    log.debug("Checking for older log files than %s in %s" % (
        last_week_date.strftime(DATE_FORMAT), LOG_DIR))
    for subdir, dirs, files in os.walk(LOG_DIR):
        for file in files:
            if file.startswith(FILE_PREFIX):
                name, created_date, _, _ = file.split("_")
                created_date = datetime.strptime(created_date, DATE_FORMAT)
                if created_date < last_week_date:
                    log.debug("deleting log file %s" % file)
                    os.remove(os.path.join(LOG_DIR, file))


def get_test_logger():
    log = logging.getLogger("testlogger")
    if not log.handlers:

        log.setLevel(logging.DEBUG)
        logFormatter = logging.Formatter("%(asctime)s | %(threadName)s | %(levelname)s | %(message)s")

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormatter)
        log.addHandler(consoleHandler)

        filehandler = logging.FileHandler(get_test_log_file_name())

        filehandler.setFormatter(logFormatter)
        log.addHandler(filehandler)

        #disabling logging for requests/urllib3
        for module_name in EXCLUDED_MODULE_LOGGING:
            logging.getLogger(module_name).setLevel(logging.WARNING)

    return log


def run_cmd(cmd):
    logger = get_logger(__name__, ENABLE_LOGFILE=True, ENABLE_CONSOLE_LOG=True, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))
    logger.debug("running cmd: %s" % cmd)
    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        logger.error('Error running command: ' + '"' + e.cmd + '"' + ' Return code: %s Output: %s' % (str(e.returncode), str(e.output)))
        return e.returncode, e.cmd
    return 0, p


def get_app_config_key(sourcefile):
    return os.path.splitext(os.path.basename(sourcefile))[0]


def delete_batch_files_in_s3(bucket_name, region, prefix=""):
    s3 = boto3.resource('s3', region)
    bucket = s3.Bucket(bucket_name)
    bucket.objects.filter(Prefix=prefix).delete()


def slugify(text):
    return re.sub(' +', '-',text.strip().lower())
