# main.py
#
# Copyright 2017 Collabora Limited
# Copyright 2017 Andrej Shadura <andrew.shadura@collabora.co.uk>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
# SPDX-License-Identifier: GPL-2.0+

import re
from urllib.error import HTTPError
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

from M2Crypto.SSL import SSLError as SSLError
from osc import conf, core, oscerr
from osc.util.helper import decode_list

from .progress import print_progress, print_status, progress, wrap_output

# python3 does not have unicode, so lets reimplement it
# as void function as it already gets unicode strings
ET_ENCODING = "unicode"


def create_project(apiurl, project, repos=[]):
    """Create a new project with sane minimal defaults."""
    tree = ET.Element('project', name=project)
    ET.SubElement(tree, 'title')
    ET.SubElement(tree, 'description')
    ET.SubElement(tree, 'person', role='maintainer', userid=conf.get_apiurl_usr(apiurl))
    ET.SubElement(tree, 'person', role='bugowner', userid=conf.get_apiurl_usr(apiurl))
    ET.SubElement(ET.SubElement(tree, 'publish'), 'disable')
    ET.SubElement(ET.SubElement(tree, 'build'), 'disable')

    repo_tags = {}
    for r in repos:
        if r.name not in repo_tags:
            repo_tags[r.name] = ET.SubElement(tree, 'repository', name=r.name)
        ET.SubElement(repo_tags[r.name], 'arch').text = r.arch

    url = core.make_meta_url(
        'prj',
        path_args=quote_plus(project),
        apiurl=apiurl,
        msg="Create %s" % project,
    )
    mf = core.metafile(url, ET.tostring(tree, encoding=ET_ENCODING))
    with wrap_output():
        mf.sync()


def mangle_metadata(metadata, src_project, dst_project, keep_metadata=False):
    if not hasattr(metadata, "splitlines"):
        metadata = b"".join(metadata)

    project = ET.fromstring(metadata)
    project.set('name', dst_project)

    if not keep_metadata:
        src_path = src_project.split(':')
        src_release, src_component = src_path[-2:]
        dst_path = dst_project.split(':')
        dst_release, dst_component = dst_path[-2:]

        for repo in project.findall('repository'):
            if repo.get('name') == src_release:
                repo.set('name', dst_release)
            for path in repo.findall('path'):
                prj_path = path.get('project').split(':')
                # mangle only distro:release:* repositories
                # FIXME: rewrite to not require confusing slices (rsplit?)
                if src_path[:-1] == prj_path[:-1]:
                    # replace distro:release: with path:to:the:new_distro:new_release:
                    path.set('project', ':'.join(dst_path[:-1] + prj_path[-1:]))
                    if path.get('repository') == src_release:
                        path.set('repository', dst_release)

        for e in project.findall('build/*') + project.findall('publish/*'):
            if e.get('repository') == src_release:
                e.set('repository', dst_release)

    return ET.tostring(project)


def increment_build_suffix(build_suffix):
    """
    Find a suitable build suffix for the next release.

    If there's a build counter, increment the letter right before it.
    If the character before it is not a letter, or if it is a 'z' already,
    insert one more letter before the build counter.

    >>> increment_build_suffix('bu')
    'bu'
    >>> increment_build_suffix('bu<B_CNT>')
    'bv<B_CNT>'
    >>> increment_build_suffix('by<B_CNT>')
    'bz<B_CNT>'
    >>> increment_build_suffix('bz<B_CNT>')
    'bza<B_CNT>'
    >>> increment_build_suffix('%%{?release_prefix}.<CI_CNT>.<B_CNT>')
    '%%{?release_prefix}.<CI_CNT>.a<B_CNT>'
    >>> increment_build_suffix('<CI_CNT>.<B_CNT>')
    '<CI_CNT>.a<B_CNT>'
    """
    m = re.match(r"(?P<prefix>[a-zA-Z0-9~%{_}<>?.+-]+?)(?P<var>[a-y]?)(?P<b_cnt><B_CNT>)(?P<rest>.*)", build_suffix)
    if not m:
        return build_suffix
    kw = m.groupdict()
    if kw['var'] == '':
        kw['var'] = 'a'
    else:
        kw['var'] = chr(ord(kw['var']) + 1)
    return "{prefix}{var}{b_cnt}{rest}".format(**kw)


def mangle_prjconf(prjconf, new_build_suffix=None):
    r"""
    Update the build suffix (Release: line) in the project configuration.

    >>> mangle_prjconf([b'Repotype: debian\n', b'type: dsc\n', b'release: bv<B_CNT>\n', b'\n'])
    ['Repotype: debian\n', 'type: dsc\n', 'release: bw<B_CNT>\n', '\n']
    >>> mangle_prjconf(['Repotype: debian\n', 'type: dsc\n', 'release: bv<B_CNT>\n', '\n'])
    ['Repotype: debian\n', 'type: dsc\n', 'release: bw<B_CNT>\n', '\n']
    >>> mangle_prjconf('Repotype: debian\ntype: dsc\nrelease: bv<B_CNT>\n\n')
    ['Repotype: debian\n', 'type: dsc\n', 'release: bw<B_CNT>\n', '\n']
    """
    def process_line(line):
        m = re.match(r"(?P<key>release):\s*(?P<value>\S+)", line.strip(), re.IGNORECASE)
        if m:
            kw = m.groupdict()
            kw['value'] = new_build_suffix or increment_build_suffix(kw['value'])
            line = "{key}: {value}\n".format(**kw)
        return line

    if hasattr(prjconf, "splitlines"):
        prjconf = prjconf.splitlines(True)
    return [process_line(line) for line in decode_list(prjconf)]


def copy_project_meta(apiurl, src_project, dst_project, keep_metadata=False, build_suffix=None):
    """
    Copy project configuration and metadata

    First update the project configuration, as it is less likely to fail.
    Then proceed with the metadata; that can fail if referenced projects
    don't exist yet.
    """
    print_status("Updating the project configuration...")
    prjconf = core.show_project_conf(apiurl, src_project)
    prjconf = mangle_prjconf(prjconf, new_build_suffix=build_suffix)
    url = core.make_meta_url(
        'prjconf',
        path_args=quote_plus(dst_project),
        apiurl=apiurl,
        msg="Update prjconf for %s" % dst_project,
    )
    mf = core.metafile(url, ''.join(prjconf))
    with wrap_output():
        mf.sync()

    print_status("Updating the project metadata...")
    metadata = core.show_project_meta(apiurl, src_project)
    metadata = mangle_metadata(metadata, src_project, dst_project, keep_metadata=keep_metadata)
    url = core.make_meta_url(
        'prj',
        path_args=quote_plus(dst_project),
        apiurl=apiurl,
        msg="Update metadata for %s" % dst_project,
    )
    mf = core.metafile(url, metadata)
    try:
        with wrap_output():
            mf.sync()
    except HTTPError as e:
        if e.hdrs.get('X-Opensuse-Errorcode') == 'unknown_project':
            e.osc_msg = "Most probably, this means some of the projects this project refers to, do not yet exist."
        raise


def do_clone(self, subcmd, opts, src_project, dst_project):
    apiurl = conf.config['apiurl']
    src_release, src_component = src_project.split(':')[-2:]
    dst_release, dst_component = dst_project.split(':')[-2:]
    try:
        src_package_list = core.meta_get_packagelist(apiurl, src_project)
    except HTTPError as e:
        if e.code == 404:
            raise oscerr.WrongOptions("Source project %s not found" % src_project)
        raise
    try:
        dst_package_list = core.meta_get_packagelist(apiurl, dst_project)
    except HTTPError as e:
        if e.code != 404:
            raise
        else:
            print_status("Destination project does not yet exist, creating...")
            create_project(apiurl, dst_project)
            dst_package_list = []

    failed_packages = set()
    succeeded_packages = set()
    todo = set(src_package_list) - set(dst_package_list)
    while set(src_package_list) - succeeded_packages:
        for package in progress(todo, desc="Copying packages..."):
            print_progress("Copying %s", "%s/%s" % (src_component, package))
            try:
                with wrap_output():
                    core.copy_pac(
                        apiurl, src_project, package,
                        apiurl, dst_project, package,
                        keep_maintainers=True,
                        expand=True,
                        comment="Branch from %s to %s" % (src_release, dst_release),
                    )
            except (oscerr.APIError, HTTPError, SSLError):
                failed_packages.add(package)
                print_status("Failed to copy %s, will retry later" % package)
                pass

        if opts.no_verify:
            verification_list = []
        else:
            verification_list = sorted(set(src_package_list) - succeeded_packages - failed_packages)
        for package in progress(verification_list, desc="Checking already copied packages..."):
            print_progress("Verifying %s", package)
            src_package_files = [
                f for f in sorted(
                    core.meta_get_filelist(
                        apiurl,
                        src_project,
                        package,
                        expand=True,
                        verbose=True,
                    ),
                    key=lambda f: f.name,
                ) if f.name != '_link'
            ]
            dst_package_files = [
                f for f in sorted(
                    core.meta_get_filelist(
                        apiurl,
                        dst_project,
                        package,
                        expand=True,
                        verbose=True,
                    ),
                    key=lambda f: f.name,
                ) if f.name != '_link'
            ]

            if len(src_package_files) != len(dst_package_files):
                print_status("Package %s not copied fully, will retry later" % package)
                failed_packages.add(package)
                continue

            for src_file, dst_file in zip(src_package_files, dst_package_files):
                if src_file.name != dst_file.name or src_file.md5 != dst_file.md5:
                    print_status("Package %s not copied fully, will retry later" % package)
                    failed_packages.add(package)
                    break
            else:
                succeeded_packages.add(package)

        todo = failed_packages
        failed_packages = set()
        if todo:
            print_status("Retrying previously failed packages...")
        elif opts.no_verify:
            break

    if not opts.copy_only:
        copy_project_meta(apiurl, src_project, dst_project, keep_metadata=opts.keep_metadata)


def mangle_prjname(name: str, src_distro: str, dst_distro: str) -> str:
    """
    Generate a new project name

    >>> mangle_prjname("apertis:v2022:development", "apertis:v2022", "apertis:v2024")
    'apertis:v2024:development'
    >>> mangle_prjname("apertis:v2022:updates:target", "apertis:v2022", "apertis:v2024")
    'apertis:v2024:updates:target'
    >>> mangle_prjname("apertis:v2022pre:updates:target", "apertis:v2022", "apertis:v2024")
    'apertis:v2022pre:updates:target'
    """
    return name.replace(src_distro + ':', dst_distro + ':')


def do_fork(self, subcmd, opts, src_distro, dst_distro):
    apiurl = conf.config['apiurl']
    projects = core.meta_get_project_list(apiurl)
    src_distro_projects = [
        p for p in projects if p.startswith(src_distro + ':')
    ]
    dst_distro_projects = [
        mangle_prjname(p, src_distro, dst_distro) for p in src_distro_projects
    ]

    if src_distro in projects:
        msg = "%s is a project" % src_distro
        if not src_distro_projects:
            msg += ", but no other related projects found"

        msg += "\n"
        msg += "Abort."

        raise oscerr.WrongArgs(msg)

    src_release = src_distro.split(':')[-1]
    dst_release = dst_distro.split(':')[-1]

    print_status("Pre-creating projects and repositories")
    for src_prj, dst_prj in zip(progress(src_distro_projects, desc="Creating projects...", unit="project"), dst_distro_projects):
        print_progress("Creating %s", dst_prj)
        repos = list(core.get_repos_of_project(apiurl, src_prj))
        if not opts.keep_metadata:
            for r in repos:
                if r.name == src_release:
                    r.name = dst_release

        create_project(apiurl, dst_prj, repos)

    opts.copy_only = True

    print_status("Copying projects")
    for src_prj, dst_prj in zip(src_distro_projects, dst_distro_projects):
        do_clone(self, subcmd, opts, src_prj, dst_prj)

    print_status("Copying metadata")
    for src_prj, dst_prj in zip(progress(src_distro_projects, desc="Copying metadata...", unit="project"), dst_distro_projects):
        copy_project_meta(apiurl, src_prj, dst_prj, keep_metadata=opts.keep_metadata)

    pass
