"""
 This file is part of Pypers.

 Pypers is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Pypers is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Pypers.  If not, see <http://www.gnu.org/licenses/>.
 """

import os
import errno
import jinja2
import sys
import shutil
import logging
import fnmatch
import time
import re
import collections
import glob
import traceback
import smtplib
import zipfile
import tarfile
import rarfile
from pyunpack import Archive
import boto3
from botocore.exceptions import ClientError
from pypers.core.interfaces import msgbus, db
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from subprocess import call, PIPE


def sort_human(list_words):
    def convert(text): return float(text) if text.isdigit() else text
    def alphanum(key): return [convert(c)
                               for c in re.split('([-+]?[0-9]*\.?[0-9]*)', key)]
    list_words.sort(key=alphanum)
    return list_words

def _get_pypers():
    current = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
    return os.environ.get('PYPERS_HOME', current)

def get_xsldir():
    return os.path.join(_get_pypers(), 'pypers', 'xsl')


def get_tmpldir():
    return os.path.join(_get_pypers(), 'pypers', 'templates')


def get_fabfile():
    return os.path.join(_get_pypers(), 'fabfile.py')


def get_fabfile7():
    return os.environ['FAB_FILE']


def get_collconf():
    return os.path.join(_get_pypers(), 'coll.yml')


def get_indexer_root():
    return os.environ['INDEXER_HOME']


def get_indexer7_root():
    return os.environ['INDEXER7_HOME']


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def mkdir_force(path):
    try:
        os.makedirs(path)
    except:
        # if dir exists, remove and recreate
        shutil.rmtree(path)
        os.makedirs(path)
    return path


"""
helper to rename files
"""
def rename_file(old_file, new_name):
    if not os.path.exists(old_file):
        return old_file

    basepath, basename = os.path.split(old_file)
    name, ext = os.path.splitext(basename)
    renamed = os.path.join(basepath, '%s%s' % (new_name, ext))
    shutil.move(old_file, renamed)

    return renamed

def ls_dir(path, regex=None, limit=0, skip=[]):
    flist = sorted(glob.glob(path))

    # filter according to regex if provided
    if regex:
        r = re.compile(regex, re.IGNORECASE)
        flist = [f for f in flist if r.match(os.path.basename(f))]

    file_list = []
    count = 0
    for fpath in flist:
        if limit and count == limit:
            break
        filename = os.path.basename(fpath)
        if filename in skip:
            continue
        file_list.append(fpath)

        count += 1

        logging.info('[ls_dir] %s: %s' % (count, fpath))

    return file_list


def validate_archive(archive, logger):
    _, ext = os.path.splitext(os.path.basename(archive))
    with open(os.devnull, 'w') as bb:
        if ext.lower() == '.rar':
            result = call(['unrar', '-t', archive], stdout=bb, stderr=bb)
            return result == 0
        elif ext.lower() == '.zip':
            zip_ref = zipfile.ZipFile(archive, 'r')
            ret = zip_ref.testzip()
            return ret is None
        elif ext.lower() == '.tar':
            result = call(['tar', 'tf', archive], stdout=bb, stderr=bb)
            return result == 0
        elif ext.lower() == '.7z':
            result = call(['7z', '-t', archive], stdout=bb, stderr=bb)
            return result == 0
        else:
            logger.warning("Could not validate %s archive because extension %s not supported" % (archive, ext))
            return True

def zipextract(archive, dest):
    try:
        zip_ref = zipfile.ZipFile(archive, 'r')
        os.makedirs(dest, exist_ok=True)
        zip_ref.extractall(dest)
        zip_ref.close()
    except Exception:
        raise Exception('Bad Zip archive: %s' % archive)


def tarextract(archive, dest):
    try:
        tar = tarfile.open(archive, 'r')
        os.makedirs(dest, exist_ok=True)
        tar.extractall(dest)
        tar.close()
    except Exception:
        raise Exception('Bad Tar archive: %s' % archive)


def rarextract(archive, dest):
    try:
        Archive(archive).extractall(dest, auto_create_dir=True)
    except Exception:
        try:
            rar = rarfile.RarFile(archive, 'r')
            rar.extractall(dest)
            rar.close()
        except Exception:
            raise Exception('Bad Rar archive: %s' % archive)


def sevenzextract(archive, dest):
    try:
        Archive(archive).extractall(dest, auto_create_dir=True)
    except Exception as e:
        logging.error(e)
        raise Exception('Bad 7z archive: %s' % archive)


def ziplist(archive):
    try:
        zip_ref = zipfile.ZipFile(archive, 'r')
        zip_lst = zip_ref.namelist()
        zip_ref.close()
        return zip_lst
    except Exception:
        raise Exception('Bad archive: %s' % archive)


def DictDiffer(dict_a, dict_b):
    for i in sorted(dict_a.keys()):
        if i not in dict_b.keys():
            return True
        if dict_a[i] != dict_b[i]:
            return True
    return False


def import_class(full_name, config_file=None):
    """
    Import the Python class `full_name` given in full Python package format,
    e.g.::

        package.another_package.class_name

    Return the imported class. Optionally, if `subclassof` is not None
    and is a Python class, make sure that the imported class is a
    subclass of `subclassof`.
    """
    # Understand which class we need to instantiate. The class name is given in
    # full Python package notation, e.g.
    #   package.subPackage.subsubpackage.className
    # in the input parameter `full_name`. This means that
    #   1. We HAVE to be able to say
    #       from package.subPackage.subsubpackage import className
    #   2. If `subclassof` is defined, the newly imported Python class MUST be a
    #      subclass of `subclassof`, which HAS to be a Python class.

    if config_file is not None:
        sys.path.insert(0, os.path.dirname(config_file))

    try:
        full_name = full_name.strip()
        package_name, sep, class_name = full_name.rpartition('.')
        if not package_name:
            raise ImportError("{0} is not a Python class".format(full_name))
        imported = __import__(
            package_name, globals(), locals(), [class_name, ], level=0)

        step_class = getattr(imported, class_name)

        if not isinstance(step_class, type):
            raise TypeError(
                'Object {0} from package {1} is not a class'.format(
                    class_name, package_name))
    finally:
        if config_file is not None:
            del sys.path[0]

    return step_class


def which(exe):
    """Find and return exe in the user unix PATH. It is meant to be the
    equivalent to the UNIX command which.

    Args:
        exe: a string containing the name of the commandline executable to find
             e.g. exe='date'

    Returns:
        A string containing the full path of the first occurrence of exe in the
        user's PATH e.g. '/bin/date'
    """
    path = os.environ.get('PATH', '')
    for directory in path.split(':'):
        if os.path.exists(os.path.join(directory, exe)):
            return os.path.join(directory, exe)
    return None


def find(directory, pattern, regex=False):
    """
    Find all the files in the directory matching the pattern
    If regex is True, the regular expression pattern matching will be used,
    otherwise the Unix filename pattern matching
    """
    match = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            fabspath = os.path.join(root, f)
            if regex:
                if re.search(pattern, f):
                    match.append(fabspath)
            else:
                if fnmatch.fnmatch(fabspath, pattern):
                    match.append(fabspath)
    return match


def find_one(directory, pattern):
    """
    Find a file matching the pattern and return
    """
    for root, dirs, files in os.walk(directory):
        for f in files:
            fabspath = os.path.join(root, f)
            if fnmatch.fnmatch(fabspath, pattern):
                return fabspath


def pretty_print(msg):
    """
    Simple logging without logger
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print("%s %s" % (now, msg))


def dict_update(d1, d2, replace=True):
    """
    Recursively update dictionary d1 with d2.
    If replace is false, only sets undefined keys
    """
    for k, v in d2.items():
        if isinstance(v, collections.Mapping):
            r = dict_update(d1.get(k, {}), v, replace)
            if replace or k not in d1:
                d1[k] = r
        else:
            if replace or k not in d1:
                d1[k] = d2[k]
    return d1


def has_write_access(dirname):
    response = False
    dirname.rstrip('/')
    while len(dirname) > 1:
        if os.path.isdir(dirname):
            if os.access(dirname, os.W_OK):
                response = True
            break
        else:
            dirname = os.path.split(dirname)[0]
    return response


def template_render(template, **var_list):
    """
    Render a jinja2 template
    """
    path = os.path.join(get_tmpldir(), template)
    print(path)
    loader = jinja2.FileSystemLoader(path)
    env = jinja2.Environment(loader=loader)
    t = env.get_template('')
    return t.render(var_list)


def send_mail(send_from, send_to, subject, text=None, html=None,
              files=None, server="127.0.0.1"):
    assert isinstance(send_to, list)

    # keep wipo recipients in the BCC
    to_adrs = [m for m in send_to if not m.endswith('@wipo.int')]

    msg = MIMEMultipart('alternative')
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(to_adrs)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    if text:
        msg.attach(MIMEText(text, 'plain'))
    if html:
        msg.attach(MIMEText(html, 'html'))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % \
                                          os.path.basename(f)
            msg.attach(part)
    if os.environ.get('GBD_DEV'):
        print("Sending email....")
        print("Subject: %s" % subject)
        print("All Dest: %s" % send_to)
        print("To: %s" % to_adrs)
        print("From: %s" % send_from)
        print("Payload: %s" % html)
    else:
        try:
            mail_client = boto3.client(
                'ses', endpoint_url=os.environ.get('SES_ENDPOINT', None))
            try:
                response = mail_client.send_raw_email(
                    Source=msg['From'],
                    Destinations=send_to,
                    RawMessage={'Data': msg.as_string()}
                )
            except ClientError as e:
                raise Exception(e.response['Error']['Message'])
        except Exception as e:
            print(e)
            db.get_db_error().send_error("Mail", "send", {},
                                         traceback.format_exc())


def notify_err(conf, logger, process_name, fetch_id, msg, files=[]):
    email_all = conf['_all_'].get('notify', {}).get('error', [])

    subject = '[%s] %s error << %s >> ' % (fetch_id, process_name, msg)
    body = 'check attachement for details'

    # send the process log file by default
    if not len(files):
        i = 0
        while i < len(logger.handlers):
            try:
                files = [logger.handlers[i].baseFilename]
                break
            except AttributeError:
                i += 1

    send_mail('webadmin@bsidx1n.wipo.int', email_all, subject,
              text=body, files=files)


def notify_success(conf, logger, fetch_id, colls, cores, files=[]):
    email_all = conf['_all_'].get('notify', {}).get('success', [])

    subject = '[%s] bnd_index.py: DONE indexing and snapshooting' % fetch_id
    body = 'data indexed for: \n\t- %s\n\n' % ('\n\t- '.join(colls))
    body += 'solr cores to be published:\n\t- %s\n' % ('\n\t- '.join(cores))
    body += '\n\ncheck attachement for details.'

    send_mail('webadmin@bsidx1n.wipo.int', email_all, subject,
              text=body, files=files)


def init_logger(log_dir, process_name, fetch_id):
    log_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5.5s]  %(message)s', '%Y-%m-%d %H:%M:%S')
    root_logger = logging.getLogger()

    # log to a file
    file_handler = logging.FileHandler(
        os.path.join(log_dir, '%s_%s.log' % (fetch_id, process_name)))
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    # log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    return root_logger


def appnum_to_subdirs(appnum):
    """
    return a properly zfilled 2 level path from the application number:
     - 0123456789 should return 67/89
     - 1 should return 00/01
    """
    appnum = appnum.zfill(4)
    subs_dir = os.path.join(appnum[-4:-2], appnum[-2:])
    return subs_dir


def appnum_to_dirs(prefix_dir, app_num):
    """
    return the prefix_dir with the properly zfilled 2 level path from
    the application number
    - prefix_dir: /data/brand-data/frtm/xml/  && appnum = 1 >
    /data/brand-data/frtm/xml/00/01/
    """
    return os.path.join(prefix_dir, appnum_to_subdirs(app_num))


def clean_folder(folder_path):
    """ Removes all the empty dirs from a given root folder"""
    for dirpath, _, _ in os.walk(folder_path, topdown=False):  # Listing the files
        if dirpath == folder_path:
            break
        try:
            os.rmdir(dirpath)
        except OSError as ex:
            pass


def delete_files(folder_path, patterns=[]):
    """ Removes all the files from  dirs following the patter"""
    regexs = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    to_remove = []
    for root, _, files in os.walk(folder_path):
        for regex in regexs:
            to_remove.extend([os.path.join(root, f) for f in files if regex.match(os.path.basename(f))])
    for f in to_remove:
        os.remove(f)


