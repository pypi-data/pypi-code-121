"""
Attributes for this project
"""

import datetime
import subprocess
import os.path
import os
import glob
import socket
import pprint


def hlp_source_under(folder):
    """
    this function finds all the python packages under a folder and
    write the 'packages' and 'package_dir' entries for a python setup.py
    script
    """
    # walk the folder and find the __init__.py entries for packages.
    packages = []
    package_dir = {}
    for root, _dirs, files in os.walk(folder):
        for file in files:
            if file != '__init__.py':
                continue
            full = os.path.dirname(os.path.join(root, file))
            relative = os.path.relpath(full, folder)
            packages.append(relative)
            package_dir[relative] = full
    # we use pprint because we want the order to always remain the same
    return f"packages={sorted(packages)},\npackage_dir={pprint.pformat(package_dir)}"


def hlp_files_under(dest_folder, pat):
    return f"('{dest_folder}', {[x for x in glob.glob(pat) if os.path.isfile(x)]})"


def make_hlp_project_keywords(d):
    def hlp_project_keywords():
        return f"{d.project_keywords.split()}"
    return hlp_project_keywords


def make_hlp_project_platforms(d):
    def hlp_project_platforms():
        return f"{d.project_platforms.split()}"

    return hlp_project_platforms


def make_hlp_project_classifiers(d):
    def hlp_project_classifiers():
        cls_list = d.project_classifiers.split('\n')
        cls_list = [x.strip()[1:-1] for x in cls_list]
        return f"{cls_list}"

    return hlp_project_classifiers


def make_hlp_wrap(level):
    def hlp_wrap(t):
        return t.replace('\n', '\n' + '\t' * level)

    return hlp_wrap


def populate(d):
    # general
    d.general_current_year = datetime.datetime.now().year
    d.general_homedir = os.path.expanduser('~')
    # d.general_hostname=subprocess.check_output(['hostname']).decode().rstrip()
    d.general_hostname = socket.gethostname()
    d.general_domainname = subprocess.check_output(['hostname', '--domain']).decode().rstrip()

    # messages
    d.messages_dne = 'THIS FILE IS AUTO GENERATED. DO NOT EDIT!!!'

    d.current_folder = os.path.basename(os.getcwd())

    # git
    try:
        d.git_describe = subprocess.check_output(['git', 'describe'], stderr=subprocess.DEVNULL).decode().rstrip()
    except subprocess.CalledProcessError:
        d.git_describe = 'no git repository'

    # this is wrong for the tag since they may not be alphabetically ordered...
    # tag=subprocess.check_output(['git', 'tag']).decode().rstrip()
    # if tag!='':
    #    d.git_lasttag=tag.split()[-1].rstrip()
    # else:
    #    d.git_lasttag='no git tag yet'

    # this is right
    try:
        d.git_lasttag = subprocess.check_output(['git', 'describe', '--abbrev=0', '--tags'],
                                                stderr=subprocess.DEVNULL).decode().rstrip()
        d.git_describe = subprocess.check_output(['git', 'describe'], stderr=subprocess.DEVNULL).decode().rstrip()
        d.git_version = '.'.join(d.git_describe.split('-'))
    except subprocess.CalledProcessError:
        d.git_lasttag = '0'
        d.git_describe = '0'
        d.git_version = '0'

    # deb
    d.deb_pkgname = os.path.basename(os.getcwd())
    # create this with 'date -R'
    # TODO: this should be created automatically here in python
    d.deb_date = 'Mon, 17 Oct 2016 09:44:00 +0300'

    # apt
    d.apt_protocol = 'https'
    d.apt_codename = subprocess.check_output(['lsb_release', '--codename', '--short']).decode().rstrip()
    d.apt_arch = subprocess.check_output('dpkg-architecture | grep -e ^DEB_BUILD_ARCH= | cut -d = -f 2',
                                         shell=True).decode().rstrip()
    d.apt_archs = f"{d.apt_arch} source"
    d.apt_component = 'main'
    d.apt_folder = 'apt'
    d.apt_service_dir = os.path.join(d.general_homedir, 'public_html/public', d.apt_folder)
    d.apt_except = f"50{d.personal_slub}"
    d.apt_pack_list = glob.glob(os.path.join(d.general_homedir, 'packages', '*.deb'))
    d.apt_packlist = ' '.join(d.apt_pack_list)
    d.apt_id = subprocess.check_output(['lsb_release', '--id', '--short']).decode().rstrip()
    d.apt_keyfile = 'public_key.gpg'
    d.apt_apache_site_file = f"{d.personal_slug}.apt"

    # helper functions
    d.hlp_source_under = hlp_source_under
    d.hlp_files_under = hlp_files_under
    d.hlp_project_keywords = make_hlp_project_keywords(d)
    d.hlp_project_platforms = make_hlp_project_platforms(d)
    d.hlp_project_classifiers = make_hlp_project_classifiers(d)
    d.make_hlp_wrap = make_hlp_wrap

    # composites
    d.deb_version = f"{d.git_version}~{d.apt_codename}"
