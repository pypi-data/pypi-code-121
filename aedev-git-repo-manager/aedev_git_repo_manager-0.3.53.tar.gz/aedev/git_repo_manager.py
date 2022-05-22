"""
create and maintain local/remote git repositories of Python projects
====================================================================

this module provides the ``grm`` tool. this document explains how to change/extend the code base of this tool.

detailed information on the installation and usage of this tool are available `in a separate user manual document
<https://aedev.readthedocs.io/en/latest/man/git_repo_manager.html>`__.


define a new action
-------------------

to add a new action you only need to declare a new method or function decorated with the :func:`_action` decorator. the
decorator will automatically register and integrate the new action into the ``grm`` tool.
"""
import ast
import os
import pprint
import re
import sys
import tempfile
import time

from collections import OrderedDict
from contextlib import contextmanager
from difflib import context_diff, diff_bytes, ndiff, unified_diff
from functools import partial, wraps
from traceback import format_exc
from typing import (
    Any, AnyStr, Callable, Collection, Dict, Iterable, Iterator, List, Optional, OrderedDict as OrderedDictType,
    Sequence, Set, Tuple, Union, cast)

from github import Github
from gitlab import Gitlab, GitlabCreateError, GitlabError, GitlabHttpError
from gitlab.const import MAINTAINER_ACCESS
from gitlab.v4.objects import Group, Project
from PIL import Image                                                                   # type: ignore
from pkg_resources import parse_version

import ae.base                                                                          # type: ignore # for patching
from ae.base import (
    PY_EXT, PY_INIT, TEMPLATES_FOLDER, UNSET, UnsetType,
    camel_to_snake, duplicates, in_wd, norm_name, norm_path, project_main_file, read_file, write_file)
from ae.paths import Collector, FilesRegister, path_files, path_folders, path_items     # type: ignore
from ae.console import ConsoleApp, sh_exec                                              # type: ignore
from ae.inspector import stack_var, try_eval                                            # type: ignore
from ae.literal import Literal                                                          # type: ignore

from aedev.setup_project import (                                                       # type: ignore
    APP_PRJ, DJANGO_PRJ, MODULE_PRJ, NO_PRJ, PACKAGE_PRJ, PARENT_PRJ, ROOT_PRJ, VERSION_PREFIX, VERSION_QUOTE,
    pev_str, pev_val, project_env_vars)


__version__ = '0.3.53'


# --------------- global constants ------------------------------------------------------------------------------------

ANY_PRJ_TYPE = (APP_PRJ, DJANGO_PRJ, MODULE_PRJ, PACKAGE_PRJ, ROOT_PRJ)
""" tuple of available project types (including the pseudo-project-types: no-/incomplete-project and parent-folder) """

ARG_MULTIPLES = ' ...'                                      #: mark multiple args in the :func:`_action` arg_names kwarg
ARG_ALL = 'all'                                             #: `all` argument, used for lists e.g. of namespace portions
ARGS_CHILDREN_DEFAULT = ((ARG_ALL, ), ('children-sets-expr', ), ('children-names' + ARG_MULTIPLES, ))
""" default arguments for children actions. """

CMD_PIP = "python -m pip"                                   #: pip command using python venvs, especially on Windows
CMD_INSTALL = f"{CMD_PIP} install"                          #: pip install command

COMMIT_MSG_FILE_NAME = '.commit_msg.txt'                    #: name of the file containing the commit message

GIT_FOLDER_NAME = '.git'                                    #: git sub-folder in project path root of local repository

NULL_VERSION = '0.0.0'                                      #: initial package version number for new project

LOCK_EXT = '.locked'                                        #: additional file extension to block updates from templates

MAIN_BRANCH = 'develop'                                     #: main/develop/default branch name

MOVE_TPL_TO_PKG_PATH_DIR_NAME_PREFIX = 'de_mtp_'
""" template folder name prefix, to move the contained templates to the package path (instead of the project path);
has to be specified after :data:`SKIP_IF_PORTION_DST_DIR_NAME_PREFIX` (if both prefixes are needed).
"""

OUTSOURCED_MARKER = 'THIS FILE IS EXCLUSIVELY MAINTAINED'   #: to mark an outsourced project file, maintained externally
OUTSOURCED_FILE_NAME_PREFIX = 'de_otf_'                     #: file name prefix of outsourced/externally maintained file

PACKAGE_VERSION_SEP = '=='                                  #: separates package name and version in pip req files

PPF = pprint.PrettyPrinter(indent=6, width=189, depth=12).pformat   #: formatter for console printouts

SKIP_PRJ_TYPE_FILE_NAME_PREFIX = 'de_spt_'                  #: file name prefix of skipped template if dst != prj type
SKIP_IF_PORTION_DST_DIR_NAME_PREFIX = 'de_sfp_'             #: skip portion prj template dst root folder name prefix

# these TEMPLATE_* constants get added by :func:`project_dev_vars` to be used/recognized by :func:`refresh_templates`
TEMPLATE_PLACEHOLDER_ID_PREFIX = "# "                       #: template id prefix marker
TEMPLATE_PLACEHOLDER_ID_SUFFIX = "#("                       #: template id suffix marker
TEMPLATE_PLACEHOLDER_ARGS_SUFFIX = ")#"                     #: template args suffix marker
TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID = "IncludeFile"        #: placeholder (func:`replace_with_file_content_or_default`)

TPL_FILE_NAME_PREFIX = 'de_tpl_'                            #: file name prefix if template contains f-strings
TPL_IMPORT_NAME_PREFIX = 'aedev.tpl_'                       #: package/import name prefix of template projects
TPL_STOP_CNV_PREFIX = '_z_'                                 #: file name prefix to support template of template

TPL_PACKAGES = [TPL_IMPORT_NAME_PREFIX + norm_name(_) for _ in ANY_PRJ_TYPE] + \
               [TPL_IMPORT_NAME_PREFIX + 'project']
""" import names of all possible template projects """

VERSION_MATCHER = re.compile("^" + VERSION_PREFIX + r"(\d+)[.](\d+)[.](\d+)[a-z\d]*" + VERSION_QUOTE, re.MULTILINE)
""" pre-compiled regular expression to detect and bump the app/portion file version numbers of a version string.

The version number format has to be :pep:`conform to PEP396 <396>` and the sub-part to `Pythons distutils
<https://docs.python.org/3/distutils/setupscript.html#additional-meta-data>`__ (trailing version information indicating
sub-releases, are either “a1,a2,…,aN” (for alpha releases), “b1,b2,…,bN” (for beta releases) or “pr1,pr2,…,prN” (for
pre-releases).
"""


ActionArgs = List[str]                                      #: action arguments specified on grm command line
ActionArgNames = Tuple[Tuple[str, ...], ...]
# ActionFunArgs = Tuple[PdvType, str, ...]                  # silly mypy does not support tuple with dict, str, ...
# silly mypy: ugly casts needed for ActionSpecification = Dict[str, Union[str, ActionArgNames, bool]]
Replacer = Callable[[str], str]

# RegisteredActionValues = Union[bool, str, ActionArgNames, Sequence[str], Callable]
RegisteredActions = Dict[str, Any]                          # silly mypy errors if using RegisteredActionValues

RegisteredTemplateProject = Dict[str, str]                  #: registered template project info (tpl_projects item)
RegisteredTemplates = Dict[str, RegisteredTemplateProject]

# PdvVarType = List[RegisteredTemplateProject]; mypy does not recognize PevType: Union[PevType, Dict[str, PdvVarType]]
PdvType = Dict[str, Any]                                    #: project development variables type
ChildrenType = OrderedDictType[str, PdvType]                #: children pdv of a project parent or a namespace root


# --------------- global variables - most of them are constant after app initialization/startup -----------------------


REGISTERED_ACTIONS: RegisteredActions = {}                  #: implemented actions registered via :func:`_action` deco

_RCS: Dict[str, Callable] = {}
""" registered recordable callees, for check* actions, using other actions with temporary redirected callees. """

REGISTERED_TPL_PROJECTS: RegisteredTemplates = {}           #: projects providing templates and outsourced files

REMOTE_CLASS_NAMES: Dict[str, str] = {}                     #: class names of all supported remote hosts

TEMP_CONTEXT: Optional[tempfile.TemporaryDirectory] = None  #: temp patch folder context (optional/lazy/late created)
TEMP_PARENT_FOLDER: str                                     #: temporary parent folder for to clone git repos into

cae = ConsoleApp(app_name="grm")                            #: main app instance of this grm tool


# --------------- dev helper functions, decorators and context managers -----------------------------------------------


def _action(*project_types: str, **deco_kwargs) -> Callable:     # Callable[[Callable], Callable]:
    """ parametrized decorator to declare functions and :class:`_RemoteHost` methods as `grm` actions. """
    if not project_types:
        project_types = ANY_PRJ_TYPE

    def _deco(fun):
        # global REGISTERED_ACTIONS
        method_of = stack_var('__qualname__')
        if 'local_action' not in deco_kwargs:
            deco_kwargs['local_action'] = not method_of
        if project_types == (PARENT_PRJ, ROOT_PRJ) and 'arg_names' not in deco_kwargs:
            deco_kwargs['arg_names'] = ARGS_CHILDREN_DEFAULT
        REGISTERED_ACTIONS[(method_of + "." if method_of else "") + fun.__name__] = {
            'annotations': fun.__annotations__, 'docstring': fun.__doc__, 'project_types': project_types, **deco_kwargs}

        @wraps(fun)
        def _wrapped(*fun_args, **fun_kwargs):  # fun_args==(self, ) for remote action methods and ==() for functions
            return fun(*fun_args, **fun_kwargs)
        return _wrapped

    return _deco


def _recordable_function(callee: Callable) -> Callable:
    """ decorator to register function as recordable (to be replaced/redirected in protocol mode). """
    _RCS[callee.__name__] = callee
    return callee


def _rc_id(instance: Any, method_name: str) -> str:
    """ compile recordable callee id of object method or module instance attribute/function. """
    return f'{getattr(instance, "__class__", instance).__name__}.{method_name}'


_RCS[_rc_id(ae.base, 'write_file')] = ae.base.write_file
_RCS[_rc_id(os, 'makedirs')] = os.makedirs


@contextmanager
def _record_calls(*recordable_methods: Any, **recordable_functions: Callable) -> Iterator[None]:
    assert len(recordable_methods) % 3 == 0, "expecting (object-or-module, method_name, callee) argument triple(s)"

    ori_callees = {}

    try:
        for obj_idx in range(0, len(recordable_methods), 3):
            instance, method_name, callee = recordable_methods[obj_idx: obj_idx + 3]
            obj_method = _rc_id(instance, method_name)
            ori_callees[obj_method] = _RCS[obj_method]
            _RCS[obj_method] = callee

        for callee_name, callee in recordable_functions.items():
            ori_callees[callee_name] = _RCS[callee_name]
            _RCS[callee_name] = callee

        yield

    finally:
        for callee_name, ori_call in ori_callees.items():
            _RCS[callee_name] = ori_call


# --------------- global helpers --------------------------------------------------------------------------------------


def activate_venv(name: str = "") -> str:
    """ ensure to activate a virtual environment if it is different to the current one (the one on Python/app start).

    :param name:                the name of the venv to activate. if this arg is empty or not specified then the venv of
                                the project in the current working directory tree will be activated.
    :return:                    the name of the previously active venv
                                or an empty string if the requested or no venv was active, or if venv is not supported.
    """
    old_name = active_venv()
    bin_path = venv_bin_path(name)
    if not old_name or not bin_path:
        if name:
            cae.dpo(f"    * the venv '{name}' does not exists - skipping switch from current venv '{old_name}'")
        else:
            cae.vpo("    # venv activation skipped, because venvs are not installed or not supported on this system")
        return ""

    activate_script_path = os.path.join(bin_path, 'activate')
    if not os.path.isfile(activate_script_path):
        cae.po(f"    * skipping venv activation, because the activate script '{activate_script_path}' does not exist")
        return ""

    new_name = bin_path.split(os.path.sep)[-2]
    if old_name == new_name:
        cae.vpo(f"    # skipped activation of venv '{new_name}' because it is already activated")
        return ""

    cae.dpo(f"    - activating venv: switching from current venv '{old_name}' to '{new_name}'")
    out: List[str] = []    # venv activation command line inspired by https://stackoverflow.com/questions/7040592
    _cl(123, f"env -i bash -c 'set -a && source {activate_script_path} && env -0'", lines_output=out)
    os.environ.update(line.split("=", maxsplit=1) for line in out[0].split("\0"))   # type: ignore

    return old_name


def active_venv() -> str:
    """ determine the virtual environment that is currently active.

    .. note:: the current venv gets set via `data:`os.environ` on start of this Python app or by :func:`activate_venv`.

    :return:                    the name of the currently active venv.
    """
    return os.getenv('VIRTUAL_ENV', "").split(os.path.sep)[-1]


def bump_file_version(file_name: str, increment_part: int = 3) -> str:
    """ increment part of version number of module/script file, also removing any pre/alpha version sub-part/suffix.

    :param file_name:           module/script file name to be patched/version-bumped.
    :param increment_part:      version number part to increment: 1=mayor, 2=minor, 3=build/revision (default=3).
    :return:                    empty string on success, else error string.
    """
    return replace_file_version(file_name, increment_part=increment_part)


def deploy_template(tpl_file_path: str, dst_path: str, patcher: str, pdv: PdvType,
                    logger: Callable = print,
                    replacer: Optional[Dict[str, Replacer]] = None,
                    dst_files: Optional[Set[str]] = None) -> bool:
    """ create/update outsourced project file content from a template.

    :param tpl_file_path:       template file path/name.ext (absolute or relative to current working directory).
    :param dst_path:            absolute or relative destination path without the destination file name. relative paths
                                are relative to the project root path (`project_path` item in :paramref:`.pdv`).
    :param patcher:             patching template project or function (to be added into the outsourced project file).
    :param pdv:                 project env/dev variables dict of the destination project to patch/refresh,
                                providing values for (1) f-string template replacements, and (2) to specify the project
                                type, and root or package data folder (in the `project_type`, and `project_path` or
                                `package_path` items).
    :param logger:              print()-like callable for logging.
    :param replacer:            optional dict with multiple replacer: key=placeholder-id and value=replacer callable.
    :param dst_files:           optional set of project file paths to be excluded from to be created/updated. if the
                                project file got created/updated by this function then the destination file path will
                                be added to this set.
    :return:                    True if template got deployed/written to the destination, else False.

    .. note::
         the project file will be kept unchanged if either:

         * the absolute file path is in :paramref:`deploy_template.dst_files`,
         * there exists a lock-file with the additional :data:`LOCK_EXT` file extension, or
         * the outsourced project text does not contain the :data:`OUTSOURCED_MARKER` string.

    """
    if replacer is None:
        replacer = {}
    if dst_files is None:
        dst_files = set()

    dst_file = os.path.basename(tpl_file_path)
    if dst_file.startswith(SKIP_PRJ_TYPE_FILE_NAME_PREFIX):
        project_type, dst_file = dst_file[len(SKIP_PRJ_TYPE_FILE_NAME_PREFIX):].split('_', maxsplit=1)
        if project_type == pdv['project_type']:
            logger(f"    - destination-project-type-skip ({project_type}) of template {tpl_file_path}")
            return False

    outsourced = dst_file.startswith(OUTSOURCED_FILE_NAME_PREFIX)
    formatting = dst_file.startswith(TPL_FILE_NAME_PREFIX)
    bin_copy = "" if outsourced or formatting else "b"

    new_content = read_file(tpl_file_path, extra_mode=bin_copy)

    if outsourced:
        new_content = _patch_outsourced(dst_file, new_content, patcher)
        dst_file = dst_file[len(OUTSOURCED_FILE_NAME_PREFIX):]
        formatting = dst_file.startswith(TPL_FILE_NAME_PREFIX)
    if formatting:
        new_content = patch_string(new_content, pdv, **replacer)
        dst_file = dst_file[len(TPL_FILE_NAME_PREFIX):]
    if dst_file.startswith(TPL_STOP_CNV_PREFIX):    # needed only for de_otf__z_de_tpl_*.* or _z_*.* template files
        dst_file = dst_file[len(TPL_STOP_CNV_PREFIX):]

    deployed = False
    dst_path = os.path.join(pdv.get('project_path', ""), dst_path)   # project_path ignored on absolute dst_path
    dst_file = norm_path(os.path.join(dst_path, patch_string(dst_file, pdv)))
    if dst_file in dst_files:
        deploy_state = "lower-priority-skip"
    else:
        dst_files.add(dst_file)
        exists = os.path.exists
        if exists(dst_file + LOCK_EXT):
            deploy_state = "lock-extension-skip"
        else:
            old_content = read_file(dst_file, extra_mode=bin_copy) if exists(dst_file) else b"" if bin_copy else ""
            if old_content and bin_copy:
                deploy_state = "binary-exists-skip"
            elif new_content == old_content:
                deploy_state = "unchanged-skip"
            elif not bin_copy and old_content and OUTSOURCED_MARKER not in old_content:
                deploy_state = "missing-outsourced-marker-skip"
            else:
                if not os.path.isdir(dst_path):
                    _RCS[_rc_id(os, 'makedirs')](dst_path)
                _RCS[_rc_id(ae.base, 'write_file')](dst_file, new_content, extra_mode=bin_copy)
                deploy_state = "refresh"
                deployed = True

    logger(f"    - {deploy_state} of template {tpl_file_path}")
    return deployed


def editable_project_path(package_name: str) -> str:
    """ determine the project path of a package installed as editable.

    :param package_name:        package/project name to search for.
    :return:                    project source root path of an editable installed package
                                or empty string if not found as editable installed package.
    """
    for install_path in sys.path:
        egg_link_file = os.path.join(install_path, package_name + '.egg-link')
        if os.path.isfile(egg_link_file):
            return read_file(egg_link_file).split(os.linesep)[0]
    return ""


def find_extra_modules(project_path: str, namespace_name: str = "", portion_name: str = "") -> List[str]:
    """ determine additional modules of a local (namespace portion) project.

    :param project_path:        file path of the local namespace project root directory/folder. passing an empty string
                                will search in the current working directory.
    :param namespace_name:      namespace name or pass an empty string for non-namespace-portion projects.
    :param portion_name:        name of the portion (folder). pass an empty string for non-namespace-portion projects.
    :return:                    list of module import name strings (without file extension and path separators as dots).
                                modules in the :data:`TEMPLATES_FOLDER` and any :data:`PY_INIT` modules are excluded.
    """
    pkg_path = norm_path(os.path.join(project_path, namespace_name, portion_name))
    if not os.path.isdir(pkg_path):
        return []

    base = os.path.basename
    rel_path = os.path.relpath
    path_sep = os.path.sep

    def _select_file(file_path: str) -> bool:
        return not rel_path(file_path, pkg_path).startswith(TEMPLATES_FOLDER + path_sep) and base(file_path) != PY_INIT

    def _create_file(file_path: str) -> str:
        return rel_path(file_path, pkg_path).replace(path_sep, '.')[:-len(PY_EXT)]

    return path_items(os.path.join(pkg_path, "**", '*' + PY_EXT), selector=_select_file, creator=_create_file)


def increment_version(version: Union[str, Iterable[str]], increment_part: int = 3) -> str:
    """ increment version number.

    :param version:             version number string or an iterable of version string parts.
    :param increment_part:      part of the version number to increment (1=mayor, 2=minor, 3=patch).
    :return:                    incremented version number.
    """
    if isinstance(version, str):
        version = version.split(".")

    return ".".join(str(int(part_str) + 1) if part_idx + 1 == increment_part else part_str
                    for part_idx, part_str in enumerate(version))


def install_requirements(req_file: str, project_path: str = ""):
    """

    :param req_file:
    :param project_path:
    :return:                    0/zero on installation without errors, else pip error return code.
    """
    project_path = norm_path(project_path)
    with _in_prj_dir_venv(project_path):
        sh_err = _cl(12, f"{CMD_INSTALL} -r {req_file}", exit_on_err=False)

    return sh_err


@contextmanager
def in_venv(name: str = "") -> Iterator[None]:
    """ ensure the virtual environment gets activated within the context.

    :param name:                the name of the venv to activate. if not specified then the venv of the project in the
                                current working directory tree will be activated.
    """
    old_venv = activate_venv(name)
    yield
    if old_venv:
        activate_venv(old_venv)


def main_file_path(project_path: str, project_type: str, namespace_name: str) -> str:
    """ return the file path of the main/version type for the specified project type.

    :param project_path:        project path, including the package name as basename.
    :param project_type:        project type to determine the main/version file path for.
    :param namespace_name:      namespace name if for namespace portion or root projects, else pass empty string.
    :return:                    main file path and name.
    """
    main_path = project_path

    main_stem = os.path.basename(project_path)
    if namespace_name:
        main_path = os.path.join(main_path, namespace_name)
        main_stem = main_stem[len(namespace_name) + 1:]

    if project_type in (PACKAGE_PRJ, ROOT_PRJ):
        main_path = os.path.join(main_path, namespace_name if project_type == ROOT_PRJ else main_stem)
        main_name = PY_INIT
    elif project_type == APP_PRJ:
        main_name = 'main' + PY_EXT
    elif project_type == DJANGO_PRJ:
        main_path = os.path.join(main_path, 'main')
        main_name = PY_INIT
    else:
        main_name = main_stem + PY_EXT

    return os.path.join(main_path, main_name)


def next_package_version(pdv: PdvType, increment_part: int = 3) -> str:
    """ determine next free package version for the project specified via the pdv argument.

    :param pdv:                 project vars to identify the package.
    :param increment_part:      part of the version number to be incremented (1=mayor, 2=minor/namespace, 3=patch).
                                pass zero/0 to return the latest published package version.
    :return:                    latest published package version as string
                                or "0.0.1" if project never published a version tag to remotes/origin
                                or empty string on error.
    """
    if _git_fetch(pdv):
        return ""

    version_tags = _git_tag_list(pdv)
    if not version_tags[-1]:
        return "0.0.1"

    return increment_version(version_tags[-1][1:], increment_part=increment_part)


def package_version(imp_or_pkg_name: str, packages_versions: List[str]) -> Sequence[str]:
    """ determine package name and version in list of package/version strings.

    :param imp_or_pkg_name:     import or package name to search.
    :param packages_versions:   package/version strings (<package_name>[<PACKAGE_VERSION_SEP><package_version>]).
    :return:                    sequence of package name and version number. the package name is an empty string if it
                                is not in :paramref:`.packages_versions`. the version number is an empty string if no
                                package version is specified in :paramref:`.packages_versions`.
    """
    package_name = norm_name(imp_or_pkg_name)
    for imp_or_pkg_name_and_ver in packages_versions:
        imp_or_pkg_name, *ver = imp_or_pkg_name_and_ver.split(PACKAGE_VERSION_SEP)
        pkg_name = norm_name(imp_or_pkg_name)
        if pkg_name == package_name:
            return package_name, ver[0] if ver else ""
    return "", ""


def patch_string(content: str, pdv: PdvType, **replacer: Replacer) -> str:
    """ replace f-string / dynamic placeholders in content with variable values / return values of replacer callables.

    :param content:             f-string to patch (e.g. a template file's content).
    :param pdv:                 project env/dev vars dict with variables used as globals for f-string replacements.
    :param replacer:            optional kwargs dict with key/name=placeholder-id and value=replacer-callable. if not
                                passed then the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID will be searched
                                and if found the callable :func:`replace_with_file_content_or_default` will be executed.
    :return:                    string extended with include snippets found in the same directory.
    :raises Exception:          if evaluation of :paramref;`~patch_string.content` f-string failed (because of
                                missing-globals-NameError/SyntaxError/ValueError/...).
    """
    glo_vars = globals().copy()     # provide globals of this module, e.g. COMMIT_MSG_FILE_NAME for .gitignore template
    glo_vars.update(pdv)
    glo_vars['_add_base_globals'] = ""
    content = try_eval('f"""' + content.replace('"""', r'\"\"\"') + '"""', glo_vars=glo_vars)
    if content:
        content = content.replace(r'\"\"\"', '"""')     # recover docstring delimiters

    for key, fun in replacer.items() or ((TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID, replace_with_file_content_or_default),):
        beg = 0
        pre = TEMPLATE_PLACEHOLDER_ID_PREFIX + key + TEMPLATE_PLACEHOLDER_ID_SUFFIX
        len_pre = len(pre)
        suf = TEMPLATE_PLACEHOLDER_ARGS_SUFFIX
        len_suf = len(suf)

        while True:
            beg = content.find(pre, beg)
            if beg == -1:
                break
            end = content.find(suf, beg)
            assert end != -1, f"patch_string() placeholder {key} is missing args suffix marker ({suf})"
            content = content[:beg] + fun(content[beg + len_pre: end]) + content[end + len_suf:]

    return content


def pdv_str(pdv: PdvType, var_name: str) -> str:
    """ string value of project development variable :paramref:`~pdv_str.var_name` of :paramref:`~pdv_str.pdv`.

    :param pdv:                 project development variables dict.
    :param var_name:            name of variable.
    :return:                    variable value or if not exists in pdv then the constant/default value of the module
                                :mod:`aedev_setup_project` or if no constant with this name exists then an empty string.
    :raises AssertionError:     if the specified variable value is not of type `str`. in this case use the function
                                :func:`pdv_val` instead.
    """
    value = pev_str(pdv, var_name)
    if not value and var_name not in pdv and _debug_or_verbose():
        cae.po(f"     # project dev variable {var_name} does not exist" + (f" in: {PPF(pdv)}" if cae.verbose else ""))
    return value


def pdv_val(pdv: PdvType, var_name: str) -> Any:        # silly mypy does not allow PdvVarType
    """ determine value of project development variable from passed pdv or :mod:`aedev_setup_project` module constant.

    :param pdv:                 project environment variables dict.
    :param var_name:            name of the variable to determine the value of.
    :return:                    project env var or module constant value. empty string if variable is not defined.
    """
    value = pev_val(pdv, var_name)
    if not value and var_name not in pdv and _debug_or_verbose():
        cae.po(f"     # project dev var value {var_name} does not exist" + (f" in: {PPF(pdv)}" if cae.verbose else ""))
    return value


def project_dev_vars(project_path: str = "") -> PdvType:
    """ analyse and map an extended project development environment, including template/root projects and git status.

    :param project_path:        optional rel/abs path of the package/app/project root directory of a new and existing
                                project (defaults to the current working directory if empty or not passed).
    :return:                    dict/mapping with the determined project development variable values.
    """
    pdv = cast(PdvType, project_env_vars(project_path=project_path))
    project_path = pdv_str(pdv, 'project_path')     # re-read as absolute path
    project_type = pdv_str(pdv, 'project_type')
    sep = os.linesep
    ins = sep + " " * 4

    pdv['editable_project_path'] = editable_project_path(pdv_str(pdv, 'package_name'))
    pdv['namespace_name'] = namespace_name = _get_namespace(pdv, project_type)  # pdv_str(pdv, 'namespace_name')
    pdv['prj_id'] = '_'.join(pdv_str(pdv, _) for _ in ('repo_domain', 'repo_group', 'package_name', 'package_version'))
    pdv['project_name'] = " ".join(pdv_str(pdv, _) for _ in ('package_name', 'project_type', 'package_version'))
    pdv['repo_group'] = _get_group(pdv)
    pdv['tpl_projects'] = tpl_projects = _template_projects(pdv)

    pdv.update({k: v for k, v in globals().items() if k.startswith('TEMPLATE_')})

    if project_type == ROOT_PRJ:
        namespace_len = len(namespace_name)
        pypi_host = pdv_str(pdv, 'PYPI_PROJECT_ROOT')

        imp_names = []
        por_vars: ChildrenType = OrderedDict()
        pypi_refs_rst = []
        pypi_refs_md = []
        for package_name_version in cast(List[str], pdv_val(pdv, 'portions_packages')):
            p_name = package_name_version.split(PACKAGE_VERSION_SEP)[0]
            portion_path = os.path.join(os.path.dirname(project_path), p_name)
            portion_name = p_name[namespace_len + 1:]
            import_name = p_name[:namespace_len] + '.' + portion_name

            pypi_refs_rst.append(f'* `{p_name} <{pypi_host}/{p_name}>`_')
            pypi_refs_md.append(f'* [{p_name}]({pypi_host}/{p_name} "{namespace_name} namespace portion {p_name}")')

            por_vars[p_name] = project_dev_vars(project_path=portion_path)

            imp_names.append(import_name)
            for e_mod in find_extra_modules(portion_path, namespace_name=namespace_name, portion_name=portion_name):
                imp_names.append(import_name + '.' + e_mod)

        pdv['children_project_vars'] = por_vars

        pdv['portions_pypi_refs'] = sep.join(pypi_refs_rst)                 # templates/..._README.rst
        pdv['portions_pypi_refs_md'] = sep.join(pypi_refs_md)               # templates/..._README.md
        pdv['portions_import_names'] = ins.join(imp_names)                  # templates/docs/..._index.rst

    elif project_type == PARENT_PRJ:
        coll = Collector(path_scanner=path_folders)
        coll.collect(project_path, select="*")
        pdv['children_project_vars'] = {os.path.basename(chi_prj_path): project_dev_vars(project_path=chi_prj_path)
                                        for chi_prj_path in coll.paths}

    elif tpl_projects and tpl_projects[0]['import_name'] == namespace_name + '.' + namespace_name:
        pdv['root_version'] = tpl_projects[0]['version']

    docs_dir = os.path.join(pdv_str(pdv, 'project_path'), pdv_str(pdv, 'DOCS_FOLDER'))
    extra_docs = path_files(os.path.join(docs_dir, "man", "**", "*.rst"))
    pdv['manuals_include'] = ""
    if extra_docs:
        pdv['manuals_include'] = f"manuals and tutorials{sep}" \
                                 f"*********************{sep}{sep}" \
                                 f".. toctree::{sep}{sep}" \
                                 f"    {ins.join(os.path.relpath(_, docs_dir) for _ in extra_docs)}"

    return pdv


def pypi_versions(package_name: str) -> List[str]:
    """ determine all the available release versions of a package hosted at the PyPI 'Cheese Shop'.

    :param package_name:        package name to get release versions from.
    :return:                    list of released versions (the latest last) or
                                on error a list with a single empty string item.
    """
    start_marker = "(from versions: "

    output: List[str] = []
    # alternative command `pip index versions {package_name}`, added in PIP v21 in June 2021 but is in March 2022 still
    # .. marked as experimental, see https://github.com/pypa/pip/pull/8978 and https://github.com/pypa/pip/issues/10052
    _cl(32, f"{CMD_INSTALL} {package_name}==non_existing_version_number", exit_on_err=False, lines_output=output)

    if len(output) >= 2 and start_marker in output[1] and start_marker + 'none' not in output[1]:
        return output[1][output[1].index(start_marker) + len(start_marker): -1].split(", ")
    return [""]


def refresh_templates(pdv: PdvType, logger: Callable = print, **replacer: Replacer) -> Set[str]:
    """ convert ae namespace package templates found in the cwd or underneath (except excluded) to the final files.

    :param pdv:                 project env/dev variables dict of the destination project to patch/refresh,
                                providing values for (1) f-string template replacements, and (2) to control the template
                                registering, patching and deployment via the variables:

                                * `namespace_name`: namespace of the destination project.
                                * 'package_name': pypi name of the package/portion/app/.. project.
                                * `package_path`: path to package data root of the destination project.
                                * `project_path`: path to working tree root of the destination project.
                                * `project_type`: type of the destination project.
                                * `repo_url`: remote/upstream repository url of the destination project.
                                * `TEMPLATES_FOLDER`: folder under the template project root, containing the templates.
                                * `tpl_projects`: template projects data (import name, project path and version).

                                .. hint:: use the function :func:`project_dev_vars` to create this dict.

    :param logger:              print()-like callable for logging.

    :param replacer:            dict of optional replacer with key=placeholder-id and value=callable.
                                if not passed then only the replacer with id TEMPLATE_INCLUDE_FILE_PLACEHOLDER_ID and
                                its callable/func :func:`replace_with_file_content_or_default` will be executed.

    :return:                    set of patched destination file names.
    """
    pdv['pypi_versions'] = pypi_versions(pdv_str(pdv, 'package_name'))
    is_portion = pdv_str(pdv, 'namespace_name') and pdv_str(pdv, 'project_type') != ROOT_PRJ
    tpl_folder = pdv_str(pdv, 'TEMPLATES_FOLDER')

    join = os.path.join
    glb = partial(path_items, recursive=True)
    isf = os.path.isfile
    dst_files: Set[str] = set()
    for tpl_prj in cast(List[RegisteredTemplateProject], pdv_val(pdv, 'tpl_projects')):
        tpl_path = join(tpl_prj['pkg_path'], tpl_folder)
        patcher = f"{tpl_prj['import_name']} V{tpl_prj['version']}"
        for tpl_file_path in [file for file in glb(join(tpl_path, "**/.*")) + glb(join(tpl_path, "**/*")) if isf(file)]:
            dst_path = os.path.relpath(os.path.dirname(tpl_file_path), tpl_path)
            if dst_path.startswith(SKIP_IF_PORTION_DST_DIR_NAME_PREFIX):
                if is_portion:
                    continue
                dst_path = dst_path[len(SKIP_IF_PORTION_DST_DIR_NAME_PREFIX):]
            if dst_path.startswith(MOVE_TPL_TO_PKG_PATH_DIR_NAME_PREFIX):
                dst_path = join(pdv_str(pdv, 'package_path'), dst_path[len(MOVE_TPL_TO_PKG_PATH_DIR_NAME_PREFIX):])

            deploy_template(tpl_file_path, dst_path, patcher, pdv,
                            logger=logger, replacer=replacer, dst_files=dst_files)

    return dst_files


def replace_file_version(file_name: str, increment_part: int = 0, new_version: str = "") -> str:
    """ replace version number of module/script file.

    :param file_name:           module/script file name to be patched/version-bumped.
    :param increment_part:      version number part to increment: 1=mayor, 2=minor, 3=build/revision, default 0=nothing.
    :param new_version:         if passed replaces the original version in the file.
    :return:                    empty string on success, else error string.
    """
    msg = f"replace_file_version({file_name}) expects "
    if not os.path.exists(file_name):
        return msg + f"existing code file path reachable from current working directory {os.getcwd()}"

    content = read_file(file_name)
    if not content:
        return msg + f"non-empty code file in {os.path.abspath(file_name)}"

    if new_version:
        _replacement = VERSION_PREFIX + increment_version(new_version, increment_part=increment_part) + VERSION_QUOTE
    else:
        def _replacement(_m):
            return VERSION_PREFIX + increment_version((_m.group(p) for p in range(1, 4)),
                                                      increment_part=increment_part) + VERSION_QUOTE
    content, replaced = VERSION_MATCHER.subn(_replacement, content)

    if replaced != 1:
        return msg + f"single occurrence of module variable {VERSION_PREFIX}{VERSION_QUOTE}, but found {replaced} times"

    _RCS[_rc_id(ae.base, 'write_file')](file_name, content)

    return ""


def replace_with_file_content_or_default(args_str: str) -> str:
    """ return file content if file name specified in first string arg exists, else return empty string or 2nd arg str.

    :param args_str:            pass either file name, or file name and default literal separated by a comma character.
                                spaces, tabs and newline characters get removed from the start and end of the file name.
                                a default literal gets parsed like a config variable, the literal value gets return.
    :return:                    file content or default literal value or empty string (if file not exists and there is
                                no comma character in :paramref:`.args_str`).
    """
    file_name, *default = args_str.split(",", maxsplit=1)
    if file_name:
        file_name = file_name.split()[0]    # strip spaces, tabs and newlines
    return read_file(file_name) if os.path.exists(file_name) else Literal(default[0]).value if default else ""


def venv_bin_path(name: str = "") -> str:
    """ determine the absolute path of the bin/executables folder of a virtual pyenv environment.

    :param name:                the name of the venv. if not specified then the venv name will be determined from the
                                first found ``.python-version`` file, starting in the current working directory (cwd)
                                and up to 3 parent directories above.
    :return:                    absolute path of the bin folder of the projects local pyenv virtual environment
    """
    venv_root = os.getenv('PYENV_ROOT')
    if not venv_root:   # pyenv is not installed
        return ""

    if not name:
        loc_env_file = '.python-version'
        for _ in range(3):
            if os.path.isfile(loc_env_file):
                name = read_file(loc_env_file).split(os.linesep)[0]
                break
            loc_env_file = ".." + os.path.sep + loc_env_file
        else:
            return ""

    return os.path.join(venv_root, 'versions', name, 'bin')

# --------------- module helpers --------------------------------------------------------------------------------------


def _act_callable(ini_pdv: PdvType, act_name: str) -> Optional[Callable]:
    return globals().get(act_name) or getattr(pdv_val(ini_pdv, 'remote_repo_api'), act_name, None)


def _available_actions(project_type: Union[UnsetType, str] = UNSET) -> Set[str]:
    return set(name.split(".")[-1] for name, data in REGISTERED_ACTIONS.items()
               if project_type is UNSET or project_type in data['project_types'])


def _act_spec(act_name: str, repo_domain: str) -> Dict[str, Any]:   # ActionSpecification
    return REGISTERED_ACTIONS.get(act_name,
                                  REGISTERED_ACTIONS.get(f"{REMOTE_CLASS_NAMES[repo_domain]}.{act_name}",
                                                         {'local_action': True}))


def _chk_if(error_code: int, check_result: bool, error_message):
    """ exit/quit this console app if the `check_result` argument is False and the `force` app option is False. """
    if not check_result:
        if cae.get_option('force'):
            cae.po(f"    # forced to ignore/skip error {error_code}: {error_message}")
        else:
            _exit_error(error_code, error_message=error_message + "\n      (specify --force to ignore/skip this error)")


def _check_commit_msg_file(pdv: PdvType) -> str:
    commit_msg_file = os.path.join(pdv_str(pdv, 'project_path'), COMMIT_MSG_FILE_NAME)
    if not os.path.isfile(commit_msg_file) or not read_file(commit_msg_file):
        _exit_error(81, f"***   missing commit message in {commit_msg_file}{_hint(prepare_commit)}")
    return commit_msg_file


def _check_folders_files_completeness(pdv: PdvType):
    changes: List[Tuple] = []

    with _record_calls(ae.base, 'write_file', lambda _dst_fn, *_, **__: changes.append(('wf', _dst_fn, _, __)),
                       os, 'makedirs', lambda _dir: changes.append(('md', _dir))):
        _renew_prj_dir(pdv)

    if changes:
        cae.po(f"  --  missing {len(changes)} basic project folders/files:")
        if cae.verbose:
            cae.po(PPF(changes))
            cae.po(f"   -- use the 'new-{pdv_str(pdv, 'project_type')}' action to re-new/complete/update this project")
        else:
            project_path = pdv_str(pdv, 'project_path')
            for change in changes:
                cae.po(f"    - {change[0] == 'md' and 'folder' or 'file  '} {os.path.relpath(change[1], project_path)}")
    elif _debug_or_verbose():
        cae.po("    = project folders and files are complete and up-to-date")


def _check_children_not_exist(parent_or_root_pdv: PdvType, *package_versions: str):
    for pkg_and_ver in package_versions:
        parent_path, pkg_and_ver = _get_parent_packageversion(parent_or_root_pdv, pkg_and_ver)
        project_path = os.path.join(parent_path, pkg_and_ver.split(PACKAGE_VERSION_SEP)[0])
        _chk_if(12, not os.path.exists(project_path), f"***   project path {project_path} does already exist")


def _check_resources_img(pdv: PdvType) -> List[str]:
    """ check images, message texts and sounds of the specified project. """
    local_images = FilesRegister(os.path.join(pdv_str(pdv, 'project_path'), "img", "**"))
    for name, files in local_images.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        _chk_if(69, not dup_files, f"duplicate image file paths for '{name}': {dup_files}")

    file_names: List[str] = []
    for name, files in local_images.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    _chk_if(69, not dup_files, f"image resources file paths duplicates: {dup_files}")

    for name, files in local_images.items():
        for file_name in (norm_path(str(file)) for file in files):
            _chk_if(69, read_file(file_name, extra_mode='b'), f"empty image resource in {file_name}")
            # noinspection PyBroadException
            try:
                img = Image.open(file_name)
                img.verify()
            except Exception as ex:
                _chk_if(69, False, f"Pillow/PIL detected corrupt image file {file_name}; exception={ex}")

    if _debug_or_verbose():
        cae.po(f"    = passed checks of {len(local_images)} image resources ({len(file_names)} files: {file_names})")

    return list(local_images.values())


def _check_resources_i18n_texts(pdv: PdvType) -> List[str]:
    file_names: List[str] = []
    messages = FilesRegister(os.path.join(pdv_str(pdv, 'project_path'), "loc", "**", "**Msg.txt"))

    for name, files in messages.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        _chk_if(69, not dup_files, f"duplicate translation messages file paths for '{name}': {dup_files}")

        for file_name in (norm_path(str(file)) for file in files):
            content = read_file(file_name)
            _chk_if(69, content, f"empty translation message file {file_name}")
            eval_texts = try_eval(content, ignored_exceptions=(Exception, ))
            texts = ast.literal_eval(content)
            _chk_if(69, eval_texts == texts, f"eval and literal_eval results differ (in file {file_name})")
            _chk_if(69, isinstance(texts, dict), f"no dict literal in {file_name}, got {type(texts)}")
            for key, text in texts.items():
                _chk_if(69, isinstance(key, str), f"file content dict keys must be strings, but got {type(key)}")
                _chk_if(69, isinstance(text, (str, dict)), f"dict values must be str|dict, got {type(text)}")
                if isinstance(text, dict):
                    for sub_key, sub_txt in text.items():
                        _chk_if(69, isinstance(sub_key, str), f"sub-dict-keys must be strings, got {type(sub_key)}")
                        typ = float if sub_key in ('app_flow_delay', 'fade_out_app', 'next_page_delay',
                                                   'page_update_delay', 'tour_start_delay', 'tour_exit_delay') else str
                        _chk_if(69, isinstance(sub_txt, typ), f"sub-dict-values of {sub_key} must be {typ}")
            file_names.append(file_name)

    dup_files = duplicates(file_names)
    _chk_if(69, not dup_files, f"translation messages file paths duplicates: {dup_files}")

    if _debug_or_verbose():
        cae.po(f"    = passed checks of {len(messages)} i18n translation texts ({len(file_names)} files: {file_names})")

    return list(messages.values())


def _check_resources_snd(pdv: PdvType) -> List[str]:
    local_sounds = FilesRegister(os.path.join(pdv_str(pdv, 'project_path'), "snd", "**"))

    for name, files in local_sounds.items():
        dup_files = duplicates(norm_path(str(file)) for file in files)
        _chk_if(69, not dup_files, f"duplicate sound file paths for '{name}': {dup_files}")

    file_names: List[str] = []
    for name, files in local_sounds.items():
        file_names.extend(norm_path(str(file)) for file in files)
    dup_files = duplicates(file_names)
    _chk_if(69, not dup_files, f"sound resources file paths duplicates: {dup_files}")

    for name, files in local_sounds.items():
        for file_name in (norm_path(str(file)) for file in files):
            _chk_if(69, read_file(file_name, extra_mode='b'), f"empty sound resource in {file_name}")

    if _debug_or_verbose():
        cae.po(f"    = passed checks of {len(local_sounds)} sound resources ({len(file_names)} files: {file_names})")

    return list(local_sounds.values())


def _check_resources(pdv: PdvType):
    """ check images, message texts and sounds of the specified project. """
    resource_files = _check_resources_img(pdv) + _check_resources_i18n_texts(pdv) + _check_resources_snd(pdv)
    if resource_files:
        cae.po(f"  === {len(resource_files)} image/message-text/sound resource file checks passed")
        if _debug_or_verbose():
            cae.po(_pp(str(_) for _ in resource_files)[1:])


def _check_templates(pdv: PdvType):
    verbose = _debug_or_verbose()
    project_path = pdv_str(pdv, 'project_path')
    rel_path = os.path.relpath

    missing: List[Tuple] = []
    outdated: List[Tuple] = []

    def _block_and_log_file_writes(dst_fn: str, content: AnyStr, extra_mode: str = ""):
        wf_args = (dst_fn, content, extra_mode)
        if not os.path.exists(dst_fn):
            missing.append(wf_args)
        else:
            old = read_file(dst_fn, extra_mode=extra_mode)
            if old != content:
                outdated.append(wf_args + (old, ))

    with _record_calls(ae.base, 'write_file', _block_and_log_file_writes,
                       os, 'makedirs', lambda _dir: None):
        checked = refresh_templates(pdv, logger=cae.po if verbose else cae.vpo)

    tpl_projects: List[RegisteredTemplateProject] = pdv_val(pdv, 'tpl_projects')
    tpl_cnt = len(tpl_projects)
    cae.dpo(f"   -- checking {tpl_cnt} of {len(REGISTERED_TPL_PROJECTS)} registered template projects: "
            + (PPF(tpl_projects) if cae.verbose else " ".join(_['import_name'] for _ in tpl_projects)))

    if missing or outdated:
        if missing:
            cae.po(f"   -- {len(missing)} outsourced files missing: "
                   + (PPF(missing) if cae.debug else " ".join(rel_path(fn, project_path) for fn, *_ in missing)))
        if outdated:
            cae.po(f"   -- {len(outdated)} outsourced files outdated: "
                   + (PPF(outdated) if cae.debug else " ".join(rel_path(fn, project_path) for fn, *_ in outdated)))
        for file_name, new_content, binary, old_content in outdated:
            cae.po(f"   -  {rel_path(file_name, project_path)}  ---")
            if verbose:
                if binary:
                    diff = cast(Iterator[str], [str(lin) for lin in diff_bytes(unified_diff, old_content, new_content)])
                elif cae.verbose:
                    diff = ndiff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True))
                else:
                    diff = context_diff(old_content.splitlines(keepends=True), new_content.splitlines(keepends=True))
            else:
                old_lines, new_lines = old_content.splitlines(keepends=True), new_content.splitlines(keepends=True)
                if cae.debug:
                    diff = unified_diff(old_lines, new_lines, n=cae.debug_level)
                else:
                    diff = cast(Iterator[str], [line for line in ndiff(old_lines, new_lines) if line[0:1].strip()])
            cae.po("      " + "      ".join(diff), end="")

        _chk_if(40, False, "***** integrity check failed. update outsourced files via the actions 'refresh' or 'renew'")

    elif checked:
        cae.po(f"  === {len(checked)} outsourced files from {tpl_cnt} template projects are up-to-date"
               + (": " + (_pp(checked) if cae.verbose else " ".join(rel_path(_, project_path) for _ in checked))
                  if verbose else ""))

    elif verbose:
        cae.po(f"   == no outsourced files found from {tpl_cnt} associated template projects")


def _check_types_linting_tests(pdv: PdvType):
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_path = pdv_str(pdv, 'project_path')
    excludes = [".buildozer"]
    mll = 120   # maximal length of code lines
    args = []
    if _debug_or_verbose():
        args.append("-v")
    if namespace_name and pdv_str(pdv, 'project_type') != ROOT_PRJ:
        args.append(namespace_name)
    else:
        args.append(pdv_str(pdv, 'version_file'))

    exclude_options = " ".join("--exclude " + _ for _ in excludes)
    with _in_prj_dir_venv(project_path):
        _cl(60, f"flake8 --max-line-length={mll} {exclude_options}", extra_args=args)

        os.makedirs("mypy_report", exist_ok=True)                               # _cl(61, "mkdir -p ./mypy_report")
        _cl(61, f"mypy {exclude_options} --lineprecision-report mypy_report"
                " --pretty --show-absolute-path --show-error-codes --show-error-context --show-column-numbers"
                " --warn-redundant-casts --warn-unused-ignores",
            extra_args=(["--namespace-packages"] if namespace_name else []) + args)
        # refactor/extend to the --strict option/level, equivalent to the following:  ( [*] == already used )
        # check-untyped-defs, disallow-any-generics, disallow-incomplete-defs, disallow-subclassing-any,
        # disallow-untyped-calls, disallow-untyped-decorators, disallow-untyped-defs, no-implicit-optional,
        # no-implicit-reexport, strict-equality, warn-redundant-casts [*], warn-return-any, warn-unused-configs,
        # warn-unused-ignores [*], """
        _cl(61, "anybadge --label=MyPy --value=passed --file=mypy_report/mypy.svg -o")

        os.makedirs(".pylint", exist_ok=True)
        out: List[str] = []
        pylint_args = ["--ignore=" + _ for _ in excludes] + [f"--max-line-length={mll}", "--output-format=text"] + args
        # alternatively to exit_on_err=False: using pylint option --exit-zero
        _cl(62, 'pylint', extra_args=pylint_args, exit_on_err=False, lines_output=out)
        if cae.get_option('verbose') and not cae.debug:
            cae.po(_pp(out))
        matcher = re.search(r"Your code has been rated at ([-\d.]*)", os.linesep.join(out))
        _chk_if(62, bool(matcher), f"   ** pylint score search failed in string {os.linesep.join(out)}")
        write_file(os.path.join(".pylint", "pylint.log"), os.linesep.join(out))
        score = matcher.group(1) if matcher else "<undetermined>"
        _cl(62, f"anybadge -o --label=Pylint --file=.pylint/pylint.svg --value={score}"
                " 2=red 4=orange 8=yellow 10=green")
        cae.po(f"  === pylint score: {score}")

        # run pytest with `python -m` to include current working dir into sys.path
        _cl(63, f"python -m pytest --cov-report html --cov={namespace_name if namespace_name else 'main'}"
                f"{' -v' if '-v' in args else ''} {pdv_str(pdv, 'TESTS_FOLDER')}/")

        sub_dir = ".pytest_cache"
        cov_db = ".coverage"
        os.makedirs(sub_dir, exist_ok=True)
        if os.path.isfile(cov_db):
            os.rename(cov_db, os.path.join(sub_dir, cov_db))
        os.chdir(sub_dir)   # KIS: move .coverage and create coverage.txt/coverage.svg in the .pytest_cache sub-dir
        out = []
        _cl(63, "coverage report", lines_output=out)    # IO fixed: .coverage/COV_CORE_DATAFILE in cwd, txt->stdout
        write_file("coverage.txt", os.linesep.join(out))
        _cl(63, "coverage-badge -o coverage.svg -f")
        cov_rep_file = f"{project_path}/htmlcov/{pdv_str(pdv, 'package_name')}_py.html"
        if not os.path.isfile(cov_rep_file):
            cov_rep_file = f"{project_path}/htmlcov/index.html"
        cae.po(f"  === pytest coverage: {out[-1][-4:]} - check detailed report in file:///{cov_rep_file}")
        os.chdir("..")

        cae.vpo(f"  --- files(hidden last) in/under {project_path}:{_pp(path_files('**/*') + path_files('**/.*'))}")


def _children_desc(pdv: PdvType, children_pdv: Collection[PdvType] = ()) -> str:
    namespace_name = pdv_str(pdv, 'namespace_name')

    ret = f"{len(children_pdv)} " if children_pdv else ""
    ret += f"{namespace_name} portions" if pdv_str(pdv, 'project_type') == ROOT_PRJ else "children"

    if children_pdv:
        ns_len = len(namespace_name)
        if ns_len:
            ns_len += 1
        ret += ": " + ", ".join(pdv_str(chi_pdv, 'package_name')[ns_len:] for chi_pdv in children_pdv)

    return ret


def _children_package_names(ini_pdv: PdvType, names: Iterable[str], chi_vars: ChildrenType) -> List[str]:
    if pdv_str(ini_pdv, 'project_type') == ROOT_PRJ:
        assert pdv_str(ini_pdv, 'namespace_name'), "namespace is not set for ROOT_PRJ"
        pkg_prefix = pdv_str(ini_pdv, 'namespace_name') + '_'
        names = [("" if por_name.startswith(pkg_prefix) else pkg_prefix) + por_name for por_name in names]

    if chi_vars:    # return children package names in the same order as in the OrderedDict 'children_project_vars' var
        ori_names = list(names)
        names = [pdv_str(chi, 'package_name') for chi in chi_vars.values() if pdv_str(chi, 'package_name') in names]
        assert len(names) == len(ori_names)

    return list(names)


def _children_path_package_option_reset():
    if cae.get_option('package'):
        cae.set_option('package', "", save_to_config=False)
    if cae.get_option('path'):
        cae.set_option('path', "", save_to_config=False)


def _cl(err_code: int, command_line: str, extra_args: Sequence = (), lines_output: Optional[List[str]] = None,
        exit_on_err: bool = True, exit_msg: str = "", shell: bool = False) -> int:
    """ execute command in the current working directory of the OS console/shell, dump error and exit app if needed.

    :param err_code:            error code to pass to console as exit code (if :paramref:`~exit_on_err` is True).
    :param command_line:        command line string to execute on the console/shell. could contain command line args
                                separated by whitespace characters (alternatively use :paramref:`~sh_exec.extra_args`).
    :param extra_args:          optional sequence of extra command line arguments.
    :param lines_output:        optional list to return the lines printed to stdout/stderr on execution.
    :param exit_on_err:         pass False to **not** exit the app on error (:paramref:`exit_msg` has then to be empty).
    :param exit_msg:            additional text to print on stdout/console if error and :paramref:`exit_on_err` is True.
    :param shell:               pass True to execute command in the default OS shell (see :meth:`subprocess.run`).
    :return:                    0 on success or the error number if an error occurred.
    """
    assert exit_on_err or not exit_msg, "specified exit message will never be shown because exit_on_err is False"
    if lines_output is None:
        lines_output = []

    sh_err = sh_exec(command_line, extra_args=extra_args, lines_output=lines_output, cae=cae, shell=shell)

    if (sh_err and exit_on_err) or cae.debug:
        for line in lines_output:
            if cae.verbose or not line.startswith("LOG:  "):    # hiding mypy's end/useless (stderr) log entries
                cae.po(f"      {line}")
        msg = f"command: {command_line} " + " ".join('"' + arg + '"' if " " in arg else arg for arg in extra_args)
        if not sh_err:
            cae.dpo(f"    = successfully executed {msg}")
        else:
            if exit_msg:
                cae.po(f"      {exit_msg}")
            _chk_if(err_code, not exit_on_err, f"  *** cl error {sh_err} in {msg}")        # app exit

    return sh_err


def _debug_or_verbose() -> bool:
    """ determine if verbose or debug option got specified (preventing on app init early call of cae.get_option()). """
    # noinspection PyProtectedMember
    return cae.debug or not cae._parsed_arguments or cae.get_option('verbose')


def _exit_error(error_code: int, error_message: str = ""):
    """ quit this shell script, optionally displaying an error message. """
    if error_code <= 9:
        cae.show_help()
    if error_message:
        cae.po(error_message)
    cae.shutdown(error_code)


def _expected_args(arg_names: ActionArgNames) -> str:
    return " -or- ".join(" ".join(_) for _ in arg_names)


def _get_branch(ini_pdv: PdvType) -> str:
    return cae.get_option('branch') or _git_current_branch(ini_pdv)


def _get_domain(ini_pdv: PdvType) -> str:
    repo_domain = cae.get_option('domain') or pdv_str(ini_pdv, 'repo_domain') or pdv_str(ini_pdv, 'REPO_CODE_DOMAIN')
    domains = tuple(REMOTE_CLASS_NAMES)
    if repo_domain not in domains:
        _exit_error(9, f"specified --remote host {repo_domain} not supported/implemented, pass {' or '.join(domains)}")
    return repo_domain


def _get_group(ini_pdv: PdvType) -> str:
    return cae.get_option('group') or pdv_str(ini_pdv, 'repo_group') or pdv_str(ini_pdv, 'STK_AUTHOR')


def _get_namespace(ini_pdv: PdvType, project_type: str) -> str:
    namespace_name = cae.get_option('namespace') or pdv_str(ini_pdv, 'namespace_name')
    if project_type == ROOT_PRJ and not namespace_name:
        _exit_error(9, "***   namespace root project expects the --namespace command line option")
    return namespace_name


def _get_package(ini_pdv: PdvType, project_type: str = NO_PRJ) -> str:
    package_name = cae.get_option('package') or pdv_str(ini_pdv, 'package_name')
    if not package_name:
        _exit_error(9, "****  missing package name (specify via the --package or --path option)")

    project_type = project_type or pdv_str(ini_pdv, 'project_type')
    namespace_name = _get_namespace(ini_pdv, project_type)
    if namespace_name and not package_name.startswith(namespace_name + '_'):
        package_name = namespace_name + '_' + package_name

    return package_name


def _get_parent_path(ini_pdv) -> str:
    parent_path = pdv_str(ini_pdv, 'project_path')
    if pdv_str(ini_pdv, 'project_type') != PARENT_PRJ:
        parent_path = os.path.dirname(parent_path)
    return parent_path


def _get_parent_packageversion(ini_pdv, package_or_portion: str) -> Tuple[str, str]:
    if package_or_portion:
        pkg_and_ver = package_or_portion
        parent_path = _get_parent_path(ini_pdv)
    else:
        parent_path, _project_path, pkg_and_ver = _get_path_package(ini_pdv)

    return parent_path, pkg_and_ver


def _get_path_package(ini_pdv: PdvType, project_type: str = NO_PRJ) -> Tuple[str, str, str]:
    parent_folders = pdv_val(ini_pdv, 'PARENT_FOLDERS')
    if project_type == NO_PRJ:
        project_type = pdv_str(ini_pdv, 'project_type')

    project_path = cae.get_option('path')       # if specified then value of cae.get_option('package') will be ignored
    if project_path:
        project_path = norm_path(project_path)
        parent_path = project_path if project_type == PARENT_PRJ else os.path.dirname(project_path)
        package_name = '' if project_type == PARENT_PRJ else os.path.basename(project_path)
    else:
        package_name = _get_package(ini_pdv, project_type=project_type)
        parent_path = _get_parent_path(ini_pdv)
        project_path = os.path.join(parent_path, package_name)

    if os.path.basename(parent_path) not in parent_folders:     # or not parent_path
        _exit_error(9, f"****  {os.path.basename(parent_path)} is not a registered parent folder ({parent_folders})")

    cae.dpo(f"    = initialized project path ({project_path}) and package ({package_name}) from command line args")

    return parent_path, project_path, package_name


def _get_renamed_path_package(ini_pdv: PdvType, namespace_name: str, project_type: str) -> Tuple[str, str]:
    _parent_path, project_path, package_name = _get_path_package(ini_pdv, project_type=project_type)
    import_name = namespace_name + '.' + package_name[len(namespace_name) + 1:] if namespace_name else package_name
    old_ns_name = pdv_str(ini_pdv, 'namespace_name')
    old_prj_type = pdv_str(ini_pdv, 'project_type')

    old_prj_path = project_path
    if old_prj_type != project_type and ROOT_PRJ in (old_prj_type, project_type):
        package_name = _get_package(ini_pdv) if old_prj_type == ROOT_PRJ else namespace_name + '_' + namespace_name
        project_path = os.path.join(os.path.dirname(project_path), package_name)
        _chk_if(6, not os.path.exists(project_path), f"  *** {project_type} root folder {project_path} exists already")

    if old_ns_name != namespace_name:
        if not old_ns_name or not namespace_name:
            _exit_error(6, f"  *** conversion from/to namespace {old_ns_name}{namespace_name} is not implemented.")
        if not cae.get_option('path'):
            _exit_error(7, f"  *** specify --path option to rename namespace from {old_ns_name} to {namespace_name}")

        new_ns_path = os.path.join(project_path, namespace_name)
        if not os.path.isdir(new_ns_path):
            os.makedirs(new_ns_path)

            if project_path == old_prj_path:
                _old = os.path.join(project_path, old_ns_name)
                if os.path.isdir(_old):
                    os.renames(_old, os.path.join(os.path.dirname(_old), "_old_" + os.path.basename(_old)))

    if old_prj_type in ANY_PRJ_TYPE and old_prj_type != project_type:
        if not cae.get_option('path'):
            _exit_error(7, f"  *** specify --path option to change project type from {old_prj_type} to {project_type}")

        _old = project_main_file(import_name, project_path=old_prj_path)
        if os.path.isfile(_old):
            _new = main_file_path(project_path, project_type, namespace_name)
            if not os.path.isdir(os.path.dirname(_new)):
                os.makedirs(os.path.dirname(_new))
            write_file(_new, read_file(_old))

            if project_path == old_prj_path:
                os.renames(_old, os.path.join(os.path.dirname(_old), "_old_" + os.path.basename(_old)))

    return project_path, package_name


def _get_user(pdv: PdvType) -> str:
    user_name = cae.get_option('gitUser')
    if user_name:
        return user_name
    repo_api = pdv_val(pdv, 'remote_repo_api')
    if repo_api:
        return repo_api.connection.user.name
    return _get_group(pdv)


@_recordable_function
def _git_add(pdv: PdvType):
    args = ["-A"]
    if _debug_or_verbose():
        args.append("-v")

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        if not _git_init_if_needed(pdv):
            _cl(31, "git add", extra_args=args)


def _git_branches(pdv: PdvType) -> List[str]:
    all_branches: List[str] = []
    project_path = pdv_str(pdv, 'project_path')
    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            _cl(27, "git branch", extra_args=("-a", "--no-color"), lines_output=all_branches)
    return [branch_name[2:] for branch_name in all_branches if cae.debug or branch_name[1] == " "]


def _git_checkout(pdv: PdvType, *extra_args: str, branch: str = "", from_branch: str = ""):
    files_uncommitted = _git_uncommitted(pdv)
    is_clean = files_uncommitted == [] or branch not in _git_branches(pdv)
    _chk_if(57, is_clean, f"   ## branch {branch} exists already and current branch {_git_current_branch(pdv)}"
                          f" has uncommitted files: {files_uncommitted}")

    args = list(extra_args)
    if branch:
        args.extend(["-B", branch])
    if from_branch:
        args.append(from_branch)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(57, "git checkout", extra_args=args)


def _git_clone(repo_root: str, package_name: str, branch_or_tag: str = "", parent_path: str = "") -> str:
    global TEMP_CONTEXT, TEMP_PARENT_FOLDER

    if not parent_path:
        if not TEMP_CONTEXT:
            TEMP_CONTEXT = tempfile.TemporaryDirectory()
            TEMP_PARENT_FOLDER = os.path.join(TEMP_CONTEXT.name, pdv_val({}, 'PARENT_FOLDERS')[-1])
            _RCS[_rc_id(os, 'makedirs')](TEMP_PARENT_FOLDER)
        parent_path = TEMP_PARENT_FOLDER

    args = []
    if _debug_or_verbose():
        args.append("-v")
    if branch_or_tag:
        # https://stackoverflow.com/questions/791959/download-a-specific-tag-with-git says:
        # .. add -b <tag> to specify a release tag/branch to clone, adding --single-branch will speed up the download
        args.append("--branch")
        args.append(branch_or_tag)
        args.append("--single-branch")
    args.append(f"{repo_root}/{package_name}.git")

    with _in_prj_dir_venv(parent_path):
        cl_err = _cl(40, "git clone", extra_args=args, exit_on_err=False)   # usr/pwd prompt if repo is private/invalid!

    return "" if cl_err else norm_path(os.path.join(parent_path, package_name))


def _git_commit(pdv: PdvType, extra_options: Iterable[str] = ()):
    """ execute the command 'git commit' for the specified project.

    :param pdv:                 providing project-name and -path in which this git command gets executed.
    :param extra_options:       additional options passed to `git commit` command line, e.g. ["--patch", "--dry-run"].

    .. note:: ensure the commit message in the file :data:`COMMIT_MSG_FILE_NAME` is uptodate.
    """
    file_name = _check_commit_msg_file(pdv)
    write_file(file_name, patch_string(read_file(file_name), pdv))
    args = [f"--file={file_name}"]
    if _debug_or_verbose():
        args.append("-v")
    args.extend(extra_options)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(82, "git commit", extra_args=args)


def _git_current_branch(pdv: PdvType) -> str:
    project_path = pdv_str(pdv, 'project_path')
    cur_branch: List[str] = []
    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            _cl(27, "git branch --show-current", lines_output=cur_branch)
    return cur_branch[0] if cur_branch else ""


def _git_diff(pdv: PdvType, *extra_opt_and_ref_specs: str) -> List[str]:
    args = ["--no-color", "--find-copies-harder", "--find-renames", "--full-index"]
    if not _debug_or_verbose():
        args.append("--compact-summary")        # alt: --name-only
    args.extend(extra_opt_and_ref_specs)

    output: List[str] = []
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(70, "git diff", extra_args=args, lines_output=output, exit_on_err=False)

    return output


def _git_fetch(pdv: PdvType, *extra_args: str) -> List[str]:
    if pdv_str(pdv, 'package_version') == NULL_VERSION:
        return []       # skip fetch preventing input of user/pw if origin remote is set but project still not pushed

    project_path = pdv_str(pdv, 'project_path')
    if not os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        return [f"missing {GIT_FOLDER_NAME} folder in '{pdv_str(pdv, 'package_name')} project root dir: {project_path}"]

    args = []
    if _debug_or_verbose():
        args.append("-v")
    args.extend(extra_args or ("--all", "--prune", "--prune-tags", "--set-upstream", "--tags"))
    # if '--all' not in args and 'origin' not in args and MAIN_BRANCH not in args:
    #    args.extend(('origin', MAIN_BRANCH))

    output: List[str] = []
    with _in_prj_dir_venv(project_path):
        _cl(75, "git fetch", extra_args=args, exit_on_err=False, lines_output=output)

    return [_ for _ in output if _[0] == "!" or 'error' in _]


def _git_init_if_needed(pdv: PdvType) -> bool:
    project_path = pdv_str(pdv, 'project_path')

    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        return False

    args = ("-v", ) if _debug_or_verbose() else ()
    with _in_prj_dir_venv(project_path):
        # next two config commands prevent error in test systems/containers
        _cl(51, "git init")
        _cl(52, "git config", extra_args=("user.email", pdv_str(pdv, 'STK_AUTHOR_EMAIL') or "CI@test.tst"))
        _cl(52, "git config", extra_args=("user.name", pdv_str(pdv, 'STK_AUTHOR') or "CiUserName"))
        _cl(55, "git checkout", extra_args=("-b", MAIN_BRANCH))
        _cl(56, "git commit", extra_args=args + ("--allow-empty", "-m", "grm repository initialization"))

    return True


def _git_merge(pdv: PdvType, from_branch: str) -> bool:
    args = [f"--file={_check_commit_msg_file(pdv)}", "--log", "--no-stat"]
    if _debug_or_verbose():
        args.append("-v")
    args.append(from_branch)

    output: List[str] = []
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(75, "git merge", extra_args=args, lines_output=output)

    return "=======" not in "".join(output)


def _git_push(pdv: PdvType, *branches_and_tags: str, exit_on_error: bool = True, extra_args: Iterable[str] = ()) -> int:
    """ push portion in the current working directory to the specified branch. """
    protocol = pdv_str(pdv, 'REPO_HOST_PROTOCOL')
    domain = _get_domain(pdv)
    package_name = _get_package(pdv)
    usr = _get_user(pdv)
    group_or_user_name = usr if 'upstream' in _git_remotes(pdv) else _get_group(pdv)
    pwd = cae.get_option('gitToken')

    args = list(extra_args)
    if cae.get_option('verbose'):
        args.append("-v")
    args.append(f"{protocol}{usr}:{pwd}@{domain}/{group_or_user_name}/{package_name}.git")
    args.extend(branches_and_tags)

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        sh_err = _cl(80, "git push", extra_args=args, exit_on_err=exit_on_error)

    return sh_err


def _git_remotes(pdv: PdvType) -> Dict[str, str]:
    project_path = pdv_str(pdv, 'project_path')
    remotes = {}
    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            remote_ids: List[str] = []
            _cl(21, "git remote", lines_output=remote_ids)
            for remote_id in remote_ids:
                remote_url: List[str] = []
                _cl(22, "git remote", extra_args=("get-url", "--push", remote_id), lines_output=remote_url)
                remotes[remote_id] = remote_url[0]
    return remotes


def _git_renew_remotes(pdv: PdvType):
    git_remotes: Dict[str, str] = _git_remotes(pdv)
    forked = 'upstream' in git_remotes
    user_or_group = _get_user(pdv) if forked else _get_group(pdv)
    origin_url = f"{pdv_str(pdv, 'REPO_HOST_PROTOCOL')}{_get_domain(pdv)}/{user_or_group}/{_get_package(pdv)}.git"

    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        if forked:
            upstream_url = pdv_str(pdv, 'repo_url') + ".git"  # adding .git prevents 'git fetch --all' redirect warning
            if git_remotes['upstream'] != upstream_url:
                _cl(41, "git remote", extra_args=("set-url", 'upstream', upstream_url))

        if 'origin' not in git_remotes:
            _cl(42, "git remote", extra_args=("add", 'origin', origin_url))
        elif git_remotes['origin'] != origin_url:
            _cl(43, "git remote", extra_args=("set-url", 'origin', origin_url))


def _git_status(pdv: PdvType) -> List[str]:
    args = ["--find-renames",  "--untracked-files=normal"]
    if cae.get_option('verbose'):
        args.append("--branch")
        args.append("-vv")
        args.append("--porcelain=2")
    else:
        args.append("-v")
        args.append("--porcelain")

    output: List[str] = []
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(75, "git status", extra_args=args, lines_output=output)

    return output


def _git_tag_add(pdv: PdvType, tag: str):
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        _cl(87, "git tag --annotate", extra_args=("--file", _check_commit_msg_file(pdv), tag))


def _git_tag_in_branch(pdv: PdvType, tag: str, branch: str = f'origin/{MAIN_BRANCH}') -> bool:
    """ check if tag/ref is in the specified or in the remote origin main branch.

    :param pdv:                 project vars.
    :param tag:                 any ref like a tag or another branch, to be searched within :paramref:`~branch`.
    :param branch:              branch to be searched in for :paramref:`~tag`.
    :return:                    True if ref got found in branch.
    """
    output: List[str] = []
    with _in_prj_dir_venv(pdv_str(pdv, 'project_path')):
        err = _cl(88, "git branch", extra_args=("--all", "--contains", tag, "--format=%(refname:short)"),
                  exit_on_err=False, lines_output=output)
    return not err and branch in output


def _git_tag_list(pdv: PdvType, tag_pattern: str = "v*") -> List[str]:
    output: List[str] = []
    project_path = pdv_str(pdv, 'project_path')
    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            _cl(89, "git tag", extra_args=("--list", "--sort=version:refname", tag_pattern), exit_on_err=False,
                lines_output=output)
    return output or [""]


def _git_uncommitted(pdv: PdvType) -> List[str]:
    output: List[str] = []
    project_path = pdv_str(pdv, 'project_path')
    if os.path.isdir(os.path.join(project_path, GIT_FOLDER_NAME)):
        with _in_prj_dir_venv(project_path):
            _cl(79, "git status", extra_args=("--find-renames",  "--untracked-files=normal", "--porcelain"),
                lines_output=output)
    return [_[3:] for _ in output]


def _hint(act_fun: Callable, run_grm_message_suffix: str = "") -> str:
    return f"{os.linesep}      (run: grm {act_fun.__name__}{run_grm_message_suffix})" if _debug_or_verbose() else ""


@contextmanager
def _in_prj_dir_venv(project_path: str, venv_name: str = "") -> Iterator[None]:
    with in_wd(project_path), in_venv(name=venv_name):
        yield


def _init_act_args_check(ini_pdv: PdvType, act_spec: Any, act_name: str, act_args: ActionArgs):
    """ check and possibly complete the command line arguments, after _init_act_exec_args/INI_PDV-initialization. """
    cae.dpo(f"   -- check args of requested action {act_name.replace('_', '-')} ({act_spec['docstring'].strip('. ')})")
    cae.vpo(f"    - action arguments: {act_args}")

    alt_arg_names = act_spec.get('arg_names')
    arg_count = len(act_args)
    if alt_arg_names:
        pos_names = []
        opt_names = []
        for arg_names in alt_arg_names:
            for arg_name in arg_names:
                if arg_name.startswith('--'):
                    opt_names.append(arg_name[2:])
                else:
                    pos_names.append(arg_name)
            pos_cnt = len(pos_names)
            pos_ok = pos_cnt <= arg_count if pos_cnt and pos_names[-1].endswith(ARG_MULTIPLES) else pos_cnt == arg_count
            if pos_ok and all(cae.get_option(opt_name) for opt_name in opt_names):
                break
        else:
            _exit_error(9, f"  **  expected arguments: {_expected_args(alt_arg_names)}")

    elif arg_count:
        _exit_error(9, f"  **  no arguments expected, but got {act_args}")

    project_type = pdv_str(ini_pdv, 'project_type')
    cae.vpo(f"    - detected project type '{project_type}' for project in {pdv_str(ini_pdv, 'project_path')}")
    if project_type not in act_spec['project_types']:
        _exit_error(33, f"  **  action '{act_name.replace('_', '-')}' only available for: {act_spec['project_types']}")

    cae.dpo("    = passed checks of basic command line options and arguments")


def _init_act_args_shortcut(ini_pdv: PdvType, ini_act_name: str) -> str:
    project_type = pdv_str(ini_pdv, 'project_type')
    found_actions = []
    for act_name, act_spec in REGISTERED_ACTIONS.items():
        if project_type in act_spec['project_types'] and act_spec.get('shortcut') == ini_act_name:
            found_actions.append(act_name.split(".")[-1])
    count = len(found_actions)
    if not count:
        return ""

    assert count in (1, 2), f"duplicate shortcut declaration for {found_actions}; correct _action() shortcut kwargs"
    if count > 1:   # happens for namespace-root project type, where action is available for project and children
        found_actions = sorted(found_actions, key=len)      # 'project'/7 is shorter than 'children'/8
    return found_actions[0]


def _init_act_exec_args() -> Tuple[PdvType, str, tuple]:
    """ prepare execution of action requested via command line arguments and options.

    * init project dev vars
    * check if action is implemented
    * check action arguments
    * run optional pre_action.

    :return:                    tuple of project pdv, action name to execute and optional action function/method args.
    """
    ini_pdv = project_dev_vars(project_path=cae.get_option('path'))

    act_name = initial_action = norm_name(cae.get_argument('action'))
    act_args = cae.get_argument('arguments').copy()
    initial_args = act_args.copy()
    project_type = pdv_str(ini_pdv, 'project_type')
    actions = _available_actions(project_type=project_type)
    while act_name not in actions:
        if not act_args:
            found_act_name = _init_act_args_shortcut(ini_pdv, initial_action)
            if found_act_name:
                act_name = found_act_name
                act_args[:] = initial_args
                break
            msg = "undefined/new projects" if project_type is NO_PRJ else f"projects of type '{project_type}'"
            _exit_error(36, f"****  invalid action '{act_name.replace('_', '-')}' for {msg}. valid actions: {actions}")
        act_name += '_' + norm_name(act_args[0])
        act_args[:] = act_args[1:]

    repo_domain = _get_domain(ini_pdv)
    act_spec = _act_spec(act_name, repo_domain)
    if not act_spec['local_action']:
        personal_token = cae.get_option('gitToken') or input("...... enter personal access token:")
        if not personal_token:
            _exit_error(37, f"****  empty git host personal access token '{personal_token}'")

        ini_pdv['remote_repo_api'] = remote_project = globals()[REMOTE_CLASS_NAMES[repo_domain]]()
        if not _act_callable(ini_pdv, act_name):
            _exit_error(38, f"****  action {act_name.replace('_', '-')} not implemented for {repo_domain}")
        if not remote_project.connect(ini_pdv, personal_token):
            _exit_error(39, f" ***  connection to {repo_domain} remote host server failed")

    _init_act_args_check(ini_pdv, act_spec, act_name, act_args)

    extra_children_args = ""
    extra_msg = ""
    if 'children_pdv' in act_spec['annotations']:   # and '_children' in act_name
        arg_count = len(act_spec['annotations']) - (2 + (1 if 'return' in act_spec['annotations'] else 0))
        if arg_count:
            extra_children_args = " <" + " ".join(_ for _ in act_args[:arg_count]) + ">"
        act_args[arg_count:] = _init_children_pdv_args(ini_pdv, act_args[arg_count:])
        extra_msg += f" :: {_children_desc(ini_pdv, children_pdv=act_args[arg_count:])}"

    pre_action = act_spec.get('pre_action')
    if pre_action:
        cae.po(f" ---- executing pre-action {pre_action.__name__.replace('_', '-')}")
        pre_action(ini_pdv, *act_args)

    cae.po(f"----- {act_name.replace('_', '-')}{extra_children_args} on {pdv_str(ini_pdv, 'project_name')}{extra_msg}")

    return ini_pdv, act_name, act_args


def _init_children_pdv_args(ini_pdv: PdvType, act_args: ActionArgs) -> List[PdvType]:
    """ get package names of the portions specified as command line args, optionally filtered by --branch option. """
    chi_vars: ChildrenType = pdv_val(ini_pdv, 'children_project_vars')

    if act_args == [ARG_ALL]:
        pkg_names = list(chi_vars)
    else:
        chi_presets = _init_children_presets(chi_vars).copy()
        pkg_names = try_eval(" ".join(act_args), (Exception, ), glo_vars=chi_presets)
        if pkg_names is UNSET:
            pkg_names = _children_package_names(ini_pdv, act_args, OrderedDict())
            cae.vpo(f"    # action arguments {act_args} are not evaluable with vars={PPF(chi_presets)}")
        else:
            pkg_names = _children_package_names(ini_pdv, pkg_names, chi_vars)

    for preset in ('filterExpression', 'filterBranch'):
        _chk_if(23, bool(cae.get_option(preset)) == any((preset in _) for _ in act_args),   # == (preset in presets)
                f"   ** mismatch of option '{preset}' and its usage in children-sets-expression {' '.join(act_args)}")
    _chk_if(23, bool(pkg_names) and isinstance(pkg_names, (list, set, tuple)),
            f"  *** empty or invalid children/portion arguments: '{act_args}' resulting in: {pkg_names}")
    _chk_if(23, len(pkg_names) == len(set(pkg_names)),
            f"   ## {len(pkg_names) - len(set(pkg_names))} duplicate children specified: {duplicates(pkg_names)}")

    return [chi_vars.get(p_name, {'package_name': p_name}) for p_name in pkg_names]


def _init_children_presets(chi_vars: ChildrenType) -> Dict[str, Set[str]]:
    branch = cae.get_option('filterBranch')
    expr = cae.get_option('filterExpression')

    chi_ps: Dict[str, Set[str]] = {}
    ps_all = chi_ps[ARG_ALL] = set()
    ps_edi = chi_ps['editable'] = set()
    ps_mod = chi_ps['modified'] = set()
    ps_dev = chi_ps['develop'] = set()
    if branch:
        chi_ps['filterBranch'] = set()
    if expr:
        chi_ps['filterExpression'] = set()

    for chi_pdv in chi_vars.values():
        package_name = pdv_str(chi_pdv, 'package_name')
        current_branch = _git_current_branch(chi_pdv)

        ps_all.add(package_name)
        if pdv_str(chi_pdv, 'editable_project_path'):
            ps_edi.add(package_name)
        if _git_uncommitted(chi_pdv):
            ps_mod.add(package_name)
        if current_branch == MAIN_BRANCH:
            ps_dev.add(package_name)
        if branch and current_branch == branch:
            chi_ps['filterBranch'].add(package_name)
        if expr:
            glo_vars = globals().copy()
            glo_vars.update(chi_pdv)
            glo_vars['chi_pdv'] = chi_pdv
            with _in_prj_dir_venv(pdv_str(chi_pdv, 'project_path')):
                result = try_eval(expr, ignored_exceptions=(Exception, ), glo_vars=glo_vars)
            if result:
                chi_ps['filterExpression'].add(package_name)
            elif result == UNSET:
                cae.vpo(f"    # filter expression {expr} not evaluable; glo_vars={PPF(glo_vars)}")

    return chi_ps


def _patch_outsourced(file_name: str, content: str, patcher: str) -> str:
    ext = os.path.splitext(file_name)[1]
    sep = os.linesep
    if ext == '.md':
        beg, end = "<!-- ", " -->"
    elif ext == '.rst':
        beg, end = f"{sep}..{sep}    ", sep
    else:
        beg, end = "# ", ""
    return f"{beg}{OUTSOURCED_MARKER} by the project {patcher}{end}{sep}{content}"


def _pp(output: Iterable[str]) -> str:
    sep = os.linesep + "      "
    return sep + sep.join(output)


def _print_pdv(pdv: PdvType):
    if not cae.get_option('verbose'):
        pdv = pdv.copy()
        pdv['setup_kwargs'] = skw = (pdv_val(pdv, 'setup_kwargs') or {}).copy()

        nsp_len = len(pdv_str(pdv, 'namespace_name')) + 1
        if pdv_str(pdv, 'project_type') in (PARENT_PRJ, ROOT_PRJ):
            pdv['children_project_vars'] = ", ".join(pdv_val(pdv, 'children_project_vars'))
        pdv['dev_require'] = ", ".join(pdv_val(pdv, 'dev_require'))
        pdv['docs_require'] = ", ".join(pdv_val(pdv, 'docs_require'))
        pdv['install_require'] = ", ".join(pdv_val(pdv, 'install_require'))
        if 'long_desc_content' in pdv:
            pdv['long_desc_content'] = skw['long_description'] = pdv_str(pdv, 'long_desc_content')[:33] + "..."
        pdv['package_data'] = ", ".join(pdv_val(pdv, 'package_data'))
        pdv['portions_packages'] = ", ".join(pkg[nsp_len:] for pkg in sorted(pdv_val(pdv, 'portions_packages')))
        pdv['project_packages'] = ", ".join(pdv_val(pdv, 'project_packages'))
        pdv['setup_require'] = ", ".join(pdv_val(pdv, 'setup_require'))
        pdv['tests_require'] = ", ".join(pdv_val(pdv, 'tests_require'))

    if not cae.verbose:
        pdv = pdv.copy()
        for name, val in list(pdv.items()):
            if not val or name in (
                    name.upper(), 'children_project_vars', 'dev_require', 'docs_require', 'import_name',
                    'install_require', 'long_desc_content', 'long_desc_type', 'namespace_name', 'package_name',
                    'package_version', 'pip_name', 'portion_name', 'portions_packages', 'portions_import_names',
                    'portions_pypi_refs', 'portions_pypi_refs_md', 'portions_project_vars',
                    'project_desc', 'project_packages', 'prj_id', 'pypi_url',
                    'repo_domain', 'repo_group', 'repo_host', 'repo_pages', 'repo_root', 'repo_url',
                    'root_version', 'setup_kwargs', 'setup_require', 'tests_require', 'tpl_projects', 'version_file'):
                pdv.pop(name, None)

    cae.po(f"      {PPF(pdv)}")


def _register_template(import_name: str, dev_require: List[str], add_req: bool, tpl_projects: list
                       ) -> RegisteredTemplateProject:
    package_name = norm_name(import_name)
    dev_req_pkg, dev_req_ver = package_version(package_name, dev_require)

    version = cae.get_option(_template_version_option(import_name))
    if not version:
        if dev_req_ver:
            version = dev_req_ver
        else:
            reg_pkg, version = package_version(package_name, list(REGISTERED_TPL_PROJECTS.keys()))
            if not reg_pkg:
                version = pypi_versions(package_name)[-1]

    key = import_name + PACKAGE_VERSION_SEP + version
    if key not in REGISTERED_TPL_PROJECTS:
        namespace_name, portion_name = import_name.split('.')
        path = ""
        if version:
            repo_root = f"https://gitlab.com/{namespace_name}-group"
            path = _git_clone(repo_root, package_name, branch_or_tag=f"v{version}")
            if path:
                path = os.path.join(path, namespace_name, portion_name)
        REGISTERED_TPL_PROJECTS[key] = {'import_name': import_name, 'pkg_path': path, 'version': version}
        if version:
            cae.vpo(f"    - {import_name} package v{version} in {path} registered as template id '{key}'")
        else:
            cae.dpo(f"    # template project {import_name} not found/registered")

    if add_req and version:
        dev_require.append(package_name + PACKAGE_VERSION_SEP + version)

    tpl_prj = REGISTERED_TPL_PROJECTS[key]
    if (add_req or dev_req_pkg) and version:
        tpl_projects.append(tpl_prj)

    return tpl_prj


def _renew_prj_dir(new_pdv: PdvType):
    namespace_name = pdv_str(new_pdv, 'namespace_name')
    package_name = pdv_str(new_pdv, 'package_name')
    project_path = pdv_str(new_pdv, 'project_path')
    project_type = pdv_str(new_pdv, 'project_type')

    is_root = project_type == ROOT_PRJ
    import_name = namespace_name + '.' + package_name[len(namespace_name) + 1:] if namespace_name else package_name

    is_file = os.path.isfile
    is_dir = os.path.isdir
    join = os.path.join
    sep = os.linesep

    sub_dir = join(project_path, pdv_str(new_pdv, 'DOCS_FOLDER'))
    if (not namespace_name or is_root) and not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    tpl_folder = pdv_str(new_pdv, 'TEMPLATES_FOLDER')
    sub_dir = join(pdv_str(new_pdv, 'package_path'), tpl_folder)
    if is_root and not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    sub_dir = join(project_path, pdv_str(new_pdv, 'TESTS_FOLDER'))
    if not is_dir(sub_dir):
        _RCS[_rc_id(os, 'makedirs')](sub_dir)

    file_name = join(project_path, pdv_str(new_pdv, 'BUILD_CONFIG_FILE'))
    if project_type == APP_PRJ and not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# {OUTSOURCED_MARKER}{sep}[app]{sep}")

    file_name = join(project_path, 'manage.py')
    if project_type == DJANGO_PRJ and not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# {OUTSOURCED_MARKER}{sep}")

    file_name = join(project_path, pdv_str(new_pdv, 'REQ_FILE_NAME'))
    if not is_file(file_name):
        _RCS[_rc_id(ae.base, 'write_file')](file_name, f"# runtime dependencies of the {import_name} project")

    main_file = project_main_file(import_name, project_path=project_path)
    if not main_file:
        main_file = main_file_path(project_path, project_type, namespace_name)
        main_path = os.path.dirname(main_file)
        if not is_dir(main_path):
            _RCS[_rc_id(os, 'makedirs')](main_path)
    if not is_file(main_file):
        _RCS[_rc_id(ae.base, 'write_file')](main_file, f"\"\"\" {package_name} {project_type} main module \"\"\"{sep}"
                                                       f"{sep}"
                                                       f"{VERSION_PREFIX}{NULL_VERSION}{VERSION_QUOTE}{sep}")


def _renew_project(ini_pdv: PdvType, project_type: str) -> PdvType:
    namespace_name = _get_namespace(ini_pdv, project_type)

    project_path, package_name = _get_renamed_path_package(ini_pdv, namespace_name, project_type)

    if not os.path.isdir(project_path):
        os.makedirs(project_path)

    version = pdv_str(ini_pdv, 'package_version') if package_name == pdv_str(ini_pdv, 'package_name') else NULL_VERSION
    new_pdv = {'namespace_name': namespace_name, 'package_name': package_name, 'package_version': version,
               'project_path': project_path, 'project_type': project_type}
    new_repo = _git_init_if_needed(new_pdv)
    action = "new" if new_repo else "renew"
    errors = update_project(new_pdv)
    _chk_if(15, not bool(errors), f" **** git fetch errors:{_pp(errors)}")

    req_branch = cae.get_option('branch')
    if req_branch or _git_current_branch(new_pdv) == MAIN_BRANCH:
        renew_branch = req_branch if req_branch and req_branch != MAIN_BRANCH else \
            f"{action}_{project_type}_{package_name}"
        co_args = ("--merge", "--track") if f"remotes/origin/{renew_branch}" in _git_branches(new_pdv) else ()
        _git_checkout(new_pdv, *co_args, branch=renew_branch)

    _renew_prj_dir(new_pdv)
    new_pdv.update(project_dev_vars(project_path=project_path))

    bump_version(new_pdv)

    dst_files = refresh_templates(new_pdv, logger=cae.po if cae.get_option('verbose') else cae.vpo)
    dbg_msg = ": " + " ".join(os.path.relpath(_, project_path) for _ in dst_files) if _debug_or_verbose() else ""
    cae.po(f"    - renewed {len(dst_files)} outsourced files{dbg_msg}")

    if new_repo:
        # also install test-requirement on first new-action (install new root dev_requirements after first publishing)
        install_requirements(os.path.join(pdv_str(new_pdv, 'TESTS_FOLDER'), pdv_str(new_pdv, 'REQ_FILE_NAME')),
                             project_path)

    new_pdv.update(project_dev_vars(project_path=project_path))

    _git_add(new_pdv)
    _git_renew_remotes(new_pdv)

    if namespace_name and project_type != ROOT_PRJ:     # is namespace portion
        _renew_local_root_req_file(new_pdv)

    cae.po(f" ==== {action} {pdv_str(new_pdv, 'project_desc')}")
    return new_pdv


def _renew_local_root_req_file(pdv: PdvType):
    namespace_name = pdv_str(pdv, 'namespace_name')
    package_name = pdv_str(pdv, 'package_name')
    req_dev_file_name = pdv_str(pdv, 'REQ_DEV_FILE_NAME')
    root_imp_name = namespace_name + '.' + namespace_name
    root_pkg_name = norm_name(root_imp_name)

    root_prj_path = os.path.join(os.path.dirname(pdv_str(pdv, 'project_path')), root_pkg_name)
    if not os.path.isdir(root_prj_path):
        cae.dpo(f"    # {namespace_name} namespace root project not found locally in {root_prj_path}")
        cae.po(f"  ### ensure to manually add {package_name} to {req_dev_file_name} of {namespace_name} namespace root")
        return

    root_req = os.path.join(root_prj_path, req_dev_file_name)
    if os.path.isfile(root_req):
        req_content = read_file(root_req)
    else:
        cae.po(f"   ## {root_req} not found in {root_imp_name} namespace root project path: creating ...")
        req_content = ""

    sep = os.linesep
    if not _required_package(package_name, req_content.split(sep)):
        if req_content and not req_content.endswith(sep):
            req_content += sep
        write_file(root_req, req_content + package_name + sep)


def _required_package(import_or_package_name: str, packages_versions: List[str]) -> bool:
    package_name, _ = package_version(import_or_package_name, packages_versions)
    return bool(package_name)


def _template_projects(pdv: PdvType) -> List[RegisteredTemplateProject]:
    """ determine template projects of namespace, project type and generic project (the highest priority first). """
    namespace_name = pdv_str(pdv, 'namespace_name')
    project_type = pdv_str(pdv, 'project_type')
    dev_require = pdv_val(pdv, 'dev_require')
    dev_req_path = os.path.join(pdv_str(pdv, 'project_path'), pdv_str(pdv, 'REQ_DEV_FILE_NAME'))
    add_req = not dev_require and not os.path.isfile(dev_req_path) and not os.path.isfile(dev_req_path + LOCK_EXT)

    tpl_projects: List[RegisteredTemplateProject] = []
    if namespace_name:
        _register_template(namespace_name + '.' + namespace_name, dev_require, add_req, tpl_projects)

    if project_type not in (PARENT_PRJ, NO_PRJ):
        _register_template(TPL_IMPORT_NAME_PREFIX + norm_name(project_type), dev_require, add_req, tpl_projects)

    _register_template(TPL_IMPORT_NAME_PREFIX + 'project', dev_require, add_req, tpl_projects)

    if _debug_or_verbose():
        cae.po(f"  --- {pdv_str(pdv, 'project_name')} uses {len(tpl_projects)} template projects:")
        cae.dpo(f"      {PPF(tpl_projects)}")
        cae.vpo(f"   -- all {len(REGISTERED_TPL_PROJECTS)} registered template projects:")
        cae.vpo(f"      {PPF(REGISTERED_TPL_PROJECTS)}")
        if add_req:
            cae.vpo(f"   -- added {len(dev_require)} template projects to {dev_req_path}: {PPF(dev_require)}")
        else:
            drt = [_ for _ in dev_require
                   if _.startswith(norm_name(TPL_IMPORT_NAME_PREFIX))
                   or _.startswith(namespace_name + '_' + namespace_name)]
            cae.vpo(f"   -- {dev_req_path} activating {len(drt)} template projects: {PPF(drt)}")

    return tpl_projects


def _template_version_option(import_name: str) -> str:
    return norm_name(import_name.split('.')[-1]) + '_version'


def _wait():
    wait_seconds = cae.get_option('delay')
    cae.po(f"..... waiting {wait_seconds} seconds")
    time.sleep(wait_seconds)


def _write_commit_message(pdv: PdvType, pkg_version: str = "{package_version}", title: str = ""):
    sep = os.linesep
    file_name = os.path.join(pdv_str(pdv, 'project_path'), COMMIT_MSG_FILE_NAME)
    if not title:
        title = _git_current_branch(pdv).replace("_", " ")
    write_file(file_name, f"V{pkg_version}: {title}{sep}{sep}{os.linesep.join(_git_status(pdv))}{sep}")


# --------------- remote repo connection ------------------------------------------------------------------------------


class _RemoteHost:
    """ base class registering subclasses as remote host repo class in :data:`REMOTES_CLASS_NAMES`. """
    def __init_subclass__(cls, **kwargs):
        """ register remote host class name; called on declaration of a subclass of :class:`_RemoteHost`. """
        # global REMOTE_CLASS_NAMES
        REMOTE_CLASS_NAMES[camel_to_snake(cls.__name__)[1:].replace('_', '.').lower()] = cls.__name__
        super().__init_subclass__(**kwargs)


class GithubCom(_RemoteHost):
    """ remote connection and actions on remote repo in gitHub.com. """
    connection: Github                  #: connection to GitHub host

    def connect(self, _ini_pdv: PdvType, personal_token: str) -> bool:
        """ connect to gitHub.com remote host.

        :param _ini_pdv:        project dev vars.
        :param personal_token:  personal token string.
        :return:                True on successful authentication else False.
        """
        try:
            self.connection = Github(personal_token)
        except (Exception, ) as ex:
            cae.po(f"****  Github connection exception: {ex}")
            return False
        return True

    # ----------- remote action methods ----------------------------------------------------------------------------

    # @_action(PARENT_PRJ, arg_names=(('fork-repo-remote-url', ), ))
    @_action(PARENT_PRJ, *ANY_PRJ_TYPE, shortcut='fork')
    def fork_project(self, ini_pdv: PdvType):
        """ create/renew fork of a remote repo specified via the ``package`` option, into our user/group namespace. """
        # group_name = _get_group(ini_pdv)
        # parent_path, _project_path, project_name = _get_path_package(ini_pdv)
        # prj = self.connection.get_repo(fork_repo_remote_url)
        # self.connection.get_user().create_fork(prj)


class GitlabCom(_RemoteHost):
    """ remote connection and actions on gitlab.com. """
    connection: Gitlab                  #: connection to Gitlab host

    def connect(self, ini_pdv: PdvType, personal_token: str) -> bool:
        """ connect to gitlab.com remote host.

        :param ini_pdv:         project dev vars.
        :param personal_token:  personal token string.
        :return:                True on successful authentication else False.
        """
        try:
            self.connection = Gitlab(pdv_str(ini_pdv, 'repo_host'), private_token=personal_token)
            if cae.debug:
                self.connection.enable_debug()
            self.connection.auth()  # authenticate and create user attribute
        except (Exception, ) as ex:
            cae.po(f"****  Gitlab connection exception: {ex}")
            return False
        return True

    def group_from_name(self, group_name: str) -> Optional[Group]:
        """ convert group/username string to remote repo user/group instance.

        :param group_name:      group name to search.
        :return:                gitlab group object/instance or None if not found.
        """
        try:
            return self.connection.groups.get(group_name)
        except GitlabError:
            groups = self.connection.groups.list(search=group_name)
        return groups[0] if groups else None                        # type: ignore

    def project_from_name(self, err_code: int, err_msg: str, project_name: str, owned: bool = True) -> Project:
        """ convert group/package_name or an endswith-fragment of it to a Project instance of the remote repo api.

        :param err_code:        error code, pass 0 to not exit on error.
        :param err_msg:         error message to display on error.
        :param project_name:    package-name, group/package-name or group/package-endswith-fragment to search for.
        :param owned:           if True then the 2nd/fallback fragment/list search is limited to owned repos (quicker).
                                pass False to search in all repos for the specified group/project-name fragment.
        :return:                python-gitlab project instance if found, else return None if err_code is zero else exit.
        """
        try:
            # Projects.get() raises GitLabError (404 project not found) on an exact project name if there are other
            # project names starting with the same string. Projects.list() will then return the project as last item.
            return self.connection.projects.get(project_name)
        except GitlabError:     # e.g. GitlabGetError: 404: 404 Project Not Found
            projects = cast(List[Project], self.connection.projects.list(search=project_name, owned=owned))

        for prj in (projects or ()):
            if prj.name.endswith(project_name):
                return prj

        if err_code:
            _exit_error(err_code, err_msg.format(name=project_name))
        elif _debug_or_verbose():
            cae.po(f"   * project {project_name} not found on connected remote server")
        return cast(Project, None)

    # ----------- remote action methods ----------------------------------------------------------------------------

    @_action()
    def clean_releases(self, ini_pdv: PdvType) -> List[str]:
        """ delete local+remote release tags and branches of the specified project that got not published to PYPI. """
        project_path = pdv_str(ini_pdv, 'project_path')
        package_name = os.path.basename(project_path)

        all_branches = _git_branches(ini_pdv)
        cae.po(f"    - found {len(all_branches)} branches to check for to be deleted: {all_branches}")

        pypi_releases = pypi_versions(pdv_str(ini_pdv, 'package_name'))
        _chk_if(34, bool(pypi_releases), "   ** no PyPI releases found (check installation of pip)")
        cae.po(f"    - found {len(pypi_releases)} PyPI release versions protected from to be deleted: {pypi_releases}")

        deleted = []
        for branch_name in all_branches:
            chk, *ver = branch_name.split('release')
            if len(ver) != 1 or ver[0] in pypi_releases:
                continue
            version = ver[0]
            if chk == 'remotes/origin/':        # un-deployed remote release branch found
                # _git_push(ini_pdv, branch_name, extra_args=("--delete", )) protected release* branch raises error
                project = self.project_from_name(33, "   ** {name} not found at origin", package_name)
                try:
                    project.protectedbranches.delete(branch_name)
                except GitlabError as ex:  # GitlabDeleteError on failed release upload
                    cae.po(f"    # try other method to delete protected branch {branch_name} on remote after err: {ex}")
                    try:
                        branch_obj = project.protectedbranches.get(branch_name)
                        branch_obj.delete()
                    except GitlabError as ex:
                        cae.po(f"   ## ignoring error deleting release branch {branch_name} on remote origin: {ex}")

                sh_err = _git_push(ini_pdv, f"v{version}", extra_args=("--delete", ), exit_on_error=False)
                if sh_err:
                    cae.po(f"   ## ignoring error {sh_err} deleting tag v{version} via push to remote")

                deleted.append(branch_name)

            elif not chk:                       # un-deployed local release branch found
                with _in_prj_dir_venv(project_path):
                    sh_err = _cl(33, f"git branch --delete {branch_name}", exit_on_err=False)
                    if sh_err:
                        cae.po(f"   ## ignoring error {sh_err} deleting branch {branch_name} via 'git branch --delete'")

                    sh_err = _cl(33, f"git tag --delete v{version}", exit_on_err=False)
                    if sh_err:
                        cae.po(f"   ## ignoring error {sh_err} deleting local tag v{version} via 'git tag --delete'")

                deleted.append(branch_name)

        cae.po(f" ==== cleaned {len(deleted)} release branches and tags: {deleted}")

        return deleted

    @_action(PARENT_PRJ, ROOT_PRJ)
    def fork_children(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ fork children of a namespace root project or of a parent folder. """
        _children_path_package_option_reset()
        for chi_pdv in children_pdv:
            self.fork_project(chi_pdv)
        cae.po(f"===== forked {_children_desc(ini_pdv, children_pdv)}")

    @_action(PARENT_PRJ, *ANY_PRJ_TYPE, shortcut='fork')
    def fork_project(self, ini_pdv: PdvType):
        """ create/renew fork of a remote repo specified via the ``package`` option, into our user/group namespace. """
        if 'upstream' in _git_remotes(ini_pdv):    # renew origin from upstream if already forked
            with _in_prj_dir_venv(pdv_str(ini_pdv, 'project_path')):
                _cl(20, f"git checkout {MAIN_BRANCH}")
                _cl(20, "git fetch upstream")
                _cl(20, f"git pull upstream {MAIN_BRANCH}")
                _cl(20, f"git push origin {MAIN_BRANCH}")
        else:
            group_name = _get_group(ini_pdv)
            parent_path, _project_path, project_name = _get_path_package(ini_pdv)
            prj_instance = self.project_from_name(20, "    * project {name} not found on remote",
                                                  f"{group_name}/{project_name}")

            prj_instance.forks.create({})        # {'namespace': usr_name}

            usr_name = self.connection.user.name                # type: ignore # silly mypy
            host_url = f"{pdv_str(ini_pdv, 'REPO_HOST_PROTOCOL')}{_get_domain(ini_pdv)}"
            with _in_prj_dir_venv(parent_path):
                _cl(21, "git clone", extra_args=(f"{host_url}/{usr_name}/{project_name}.git", ))
                _cl(21, "git remote", extra_args=("add", 'upstream', f"{host_url}/{group_name}/{project_name}.git"))
                _git_renew_remotes(ini_pdv)     # add/renew git remote origin

        _git_checkout(ini_pdv, branch=_get_branch(ini_pdv))
        cae.po(f" ==== forked {pdv_str(ini_pdv, 'project_desc')}")

    @_action(PARENT_PRJ, ROOT_PRJ, shortcut='push')
    def push_children(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ push specified children projects to remotes/origin. """
        for chi_pdv in children_pdv:
            self.push_project(chi_pdv)
            if chi_pdv != children_pdv[-1]:
                _wait()
        cae.po(f"===== pushed {_children_desc(ini_pdv, children_pdv)}")

    @_action(arg_names=((), ('branch-name', ), ), shortcut='push')
    def push_project(self, ini_pdv: PdvType, branch_name: str = ''):
        """ push current/specified branch of project/package to remote domain, version-tagged if release is True.

        :param ini_pdv:             project dev vars.
        :param branch_name:         optional branch name to push (alternatively specified by the ``branch`` command line
                                    option).
        """
        package_name = _get_package(ini_pdv)

        changed = _git_uncommitted(ini_pdv)
        _chk_if(76, not changed, f"   ** {package_name} has {len(changed)} uncommitted files: {changed}")

        push_refs = []
        if not self.project_from_name(0, "", package_name):
            group_name = _get_group(ini_pdv)
            project_properties = {
                'name': package_name,
                'namespace_id': self.group_from_name(group_name).id,        # type: ignore
                'description': pdv_str(ini_pdv, 'project_desc'),
                'default_branch': MAIN_BRANCH,
                'visibility': 'public',
            }
            cae.vpo(f"    - remote project properties of new package {package_name}: {PPF(project_properties)}")
            project = cast(Project, self.connection.projects.create(project_properties))

            cae.po(f"   == created new project {PPF(project.attributes)} under remote user/group {group_name}")
            _wait()

            for branch_mask in (MAIN_BRANCH, 'release*'):
                protected_branch_properties = {'name': branch_mask,
                                               'merge_access_level': MAINTAINER_ACCESS,
                                               'push_access_level': MAINTAINER_ACCESS}
                cae.vpo(f"    - {branch_mask} protected branch properties: {protected_branch_properties}")
                project.protectedbranches.create(protected_branch_properties)
            cae.po(f"   == protected branches {MAIN_BRANCH} and release*")

            push_refs.append(MAIN_BRANCH)

        branch_name = branch_name or _get_branch(ini_pdv)
        if branch_name and branch_name not in push_refs:
            push_refs.append(branch_name)

        pkg_version = next_package_version(ini_pdv, increment_part=cae.get_option('versionIncrementPart'))
        file_version = pdv_str(ini_pdv, 'package_version')
        _chk_if(77, pkg_version == file_version, f"   ** version mismatch: local={file_version} remote={pkg_version}")
        if parse_version(pkg_version) > parse_version(file_version):     # and cae.get_option('force')
            replace_file_version(pdv_str(ini_pdv, 'version_file'), new_version=pkg_version)
            _write_commit_message(ini_pdv, pkg_version=pkg_version,
                                  title=f"late commit of forced push version correction {file_version}->{pkg_version}")
            _git_add(ini_pdv)
            _git_commit(ini_pdv)
            ini_pdv['package_version'] = pkg_version
        else:
            pkg_version = file_version
        tag = f"v{pkg_version}"
        _git_tag_add(ini_pdv, tag)
        push_refs.append(tag)

        _git_push(ini_pdv, *push_refs, extra_args=("--set-upstream", ))

        cae.po(f" ==== pushed {' '.join(push_refs)} branches/tags to remote project {package_name}")

    @_action(PARENT_PRJ, ROOT_PRJ, shortcut='release')
    def release_children(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ release the latest versions of the specified parent/root children projects to remotes/origin. """
        for chi_pdv in children_pdv:
            cae.po(f" ---  {pdv_str(chi_pdv, 'package_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
            self.release_project(chi_pdv, 'LATEST')
            if chi_pdv != children_pdv[-1]:
                _wait()
        cae.po(f"===== released {_children_desc(ini_pdv, children_pdv)}")

    @_action(arg_names=(("push-tag", ), ('LATEST',)), shortcut='release')
    def release_project(self, ini_pdv: PdvType, push_tag: str):
        """ release the specified/latest develop push commit tag.

        :param ini_pdv:         project dev vars.
        :param push_tag:        push version tag in the format 'v<version-number>' to release or ``LATEST`` to use
                                the version tag of the latest push.
        """
        errors = _git_fetch(ini_pdv)
        _chk_if(84, not bool(errors), f" **** git fetch errors:{_pp(errors)}" + _hint(
            self.release_project, " later to retry if server is currently unavailable, or check remote configuration"))

        # switch back to local MAIN_BRANCH and then merge-in the release-branch&-tag from remotes/origin/MAIN_BRANCH
        _git_checkout(ini_pdv, branch=MAIN_BRANCH)
        _git_merge(ini_pdv, f"origin/{MAIN_BRANCH}")

        if push_tag == 'LATEST':
            pkg_version = next_package_version(ini_pdv, increment_part=0)
            push_tag = f"v{pkg_version}"
        else:
            _chk_if(85, push_tag[0] == "v" and push_tag.count(".") == 2, f"   ** push tag format error {push_tag}")
            pkg_version = push_tag[1:]
        _chk_if(85, _git_tag_in_branch(ini_pdv, push_tag),
                f"    * push version tag {push_tag} has first to be merged into origin/{MAIN_BRANCH}" + _hint(
                    self.request_merge, " to request to merge your branch."))

        release_branch = f"release{pkg_version}"
        _chk_if(85, not _git_tag_in_branch(ini_pdv, release_branch),
                f"    * release branch {release_branch} already exists in origin/{MAIN_BRANCH}")

        prj = self.project_from_name(95, "    * project {name} not found", pdv_str(ini_pdv, 'package_name'))
        cae.dpo(f"   -- creating branch '{release_branch}' for tag '{push_tag}' at remotes/origin")
        try:
            prj.branches.create({'branch': release_branch, 'ref': push_tag})
        except (GitlabHttpError, GitlabCreateError, GitlabError, Exception):
            _exit_error(86, f"  *** exception {format_exc()} creating branch '{release_branch}' for tag '{push_tag}'")
        cae.po(f" ==== released {pdv_str(ini_pdv, 'project_desc')}")

    @_action(PARENT_PRJ, ROOT_PRJ, shortcut='request')
    def request_children_merge(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ request the merge of the specified children of a parent/namespace on remote/upstream. """
        for chi_pdv in children_pdv:
            cae.po(f" ---  {pdv_str(chi_pdv, 'package_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
            self.request_merge(chi_pdv)
            if chi_pdv != children_pdv[-1]:
                _wait()
        cae.po(f"===== requested merge of {_children_desc(ini_pdv, children_pdv)}")

    @_action(shortcut='request')
    def request_merge(self, ini_pdv: PdvType):
        """ request merge of the origin=fork repository into the main branch at remote/upstream=forked. """
        branch = _get_branch(ini_pdv)
        group_name = _get_group(ini_pdv)
        user_name = _get_user(ini_pdv)
        package_name = _get_package(ini_pdv)

        remotes = _git_remotes(ini_pdv)
        origin_user = remotes.get('origin', "/").split('/')[-2]
        _chk_if(64, origin_user == user_name, f"   ** user mismatch specified={user_name} != origin={origin_user}")
        upstream_group = remotes.get('upstream', "/").split('/')[-2]
        _chk_if(65, upstream_group == group_name, f"   ** group mismatch spe={group_name} != upstream={upstream_group}")

        # https://docs.gitlab.com/ee/api/merge_requests.html#create-mr and https://stackoverflow.com/questions/51104622
        # target_project_id/project_id is the upstream and source_project_id is the origin/fork
        src_prj = self.project_from_name(65, " **** origin/fork repository {name} not found on remote server",
                                         f"{user_name}/{package_name}")
        tgt_prj = self.project_from_name(66, " **** target/upstream/forked repository {name} not found on remote",
                                         f"{group_name}/{package_name}")

        commit_msg_file = _check_commit_msg_file(ini_pdv)
        merge_req = tgt_prj.mergerequests.create({
            'project_id': tgt_prj.id,
            'source_project_id': src_prj.id,
            'source_branch': branch,
            'target_project_id': tgt_prj.id,
            'target_branch': MAIN_BRANCH,
            'title': read_file(commit_msg_file).split(os.linesep)[0],
            # 'remove_source_branch': False,
            # 'force_remove_source_branch': False,
            # 'allow_collaboration': True,
            # 'subscribed': True,
        })
        if _debug_or_verbose():
            cae.po(f"    . merge request diffs: {PPF([_.attributes for _ in merge_req.diffs.list()])}")

        action = "requested merge"
        if cae.get_option('force') and user_name == group_name:
            _wait()     # wait for created un-forked/direct maintainer merge request (with --force --gitUser=group_name)
            merge_req.merge(merge_commit_message=read_file(_check_commit_msg_file(ini_pdv)))
            action = "auto-merged un-forked and forced merge request"
        cae.po(f" ==== {action} of branch {branch} from fork/origin ({src_prj.id}) into upstream ({tgt_prj.id})")

    @_action()
    def search_repos(self, ini_pdv: PdvType):
        """ search remote repositories via group/package name fragment. """
        group_name = _get_group(ini_pdv)
        package_name = _get_package(ini_pdv)
        fragment = f"{group_name}/{package_name}" if group_name and package_name else group_name or package_name
        repos = self.connection.projects.list(search=fragment, owned=True)
        cae.po(f"----  found {len(repos)} project repositories containing {fragment}:")
        for repo in repos:
            cae.po(PPF(repo))
        cae.po(f" ==== searched {pdv_str(ini_pdv, 'project_desc')}")

    @_action(PARENT_PRJ, ROOT_PRJ)
    def show_children_repos(self, ini_pdv: PdvType, *children_pdv: PdvType):
        """ display remote properties of parent/root children repos. """
        for chi_pdv in children_pdv:
            self.show_repo(chi_pdv)
        cae.po(f"===== dumped info of {_children_desc(ini_pdv, children_pdv)}")

    @_action()
    def show_repo(self, ini_pdv: PdvType):
        """ display properties of remote repository. """
        group_project = f"{_get_group(ini_pdv)}/{_get_package(ini_pdv)}"
        repo_api = self.project_from_name(0, "", group_project)
        if isinstance(repo_api, Project):
            cae.po(f"   -- {group_project} remote repository attributes:")
            for attr in sorted(repo_api.attributes) if _debug_or_verbose() else \
                    ('created_at', 'default_branch', 'description', 'id', 'path_with_namespace', 'visibility'):
                cae.po(f"    - {attr} = {getattr(repo_api, attr, None)}")

            cae.po(f"   -- protected branches = {PPF(repo_api.protectedbranches.list())}")
            cae.po(f"   -- protected tags = {PPF(repo_api.protectedtags.list())}")
        else:
            cae.po(f"    * project {group_project} not found on remote server")
        cae.po(f" ==== dumped repo info of {pdv_str(ini_pdv, 'project_desc')}")


# --------------- local actions ---------------------------------------------------------------------------------------


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('source-name', 'rel-path', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def add_children_file(ini_pdv: PdvType, file_name: str, rel_path: str, *children_pdv: PdvType) -> bool:
    """ add a file, template of outsourced text file to the working trees of parent/root and children/portions.

    :param ini_pdv:             parent/root project dev vars.
    :param file_name:           source (template) file name (optional with path).
    :param rel_path:            relative destination path within the working tree.
    :param children_pdv:        project dev vars of the children to process.
    :return:                    True if the file got added to the parent/root and to all children, else False.
    """
    added = []
    is_root = pdv_str(ini_pdv, 'project_type') == ROOT_PRJ
    if is_root and add_file(ini_pdv, file_name, rel_path):
        added.append(pdv_str(ini_pdv, 'package_name'))

    for chi_pdv in children_pdv:
        if add_file(chi_pdv, file_name, rel_path):
            added.append(pdv_str(chi_pdv, 'package_name'))

    cae.po(f"===== added {len(added)}/{len(children_pdv)} times {file_name} into {rel_path} for: {added}")
    return len(added) == (1 if is_root else 0) + len(children_pdv)


@_action(arg_names=(('source-name', 'rel-path', ), ))
def add_file(ini_pdv: PdvType, file_name: str, rel_path: str) -> bool:
    """ add file, template or outsourced text file into the project working tree.

    :param ini_pdv:             project dev vars.
    :param file_name:           file name to add (optional with abs. path, else relative to working tree root folder).
    :param rel_path:            relative path in destination project working tree.
    :return:                    True if the file got added to the specified project, else False.
    """
    project_path = pdv_str(ini_pdv, 'project_path')
    file_name = os.path.join(project_path, file_name)
    dst_dir = os.path.join(project_path, rel_path)
    if not os.path.isfile(file_name) or not os.path.isdir(dst_dir):
        cae.dpo(f"  ### either source file {file_name} or destination folder {dst_dir} does not exist")
        return False

    if any(os.path.basename(file_name).startswith(_) for _ in (
            TPL_FILE_NAME_PREFIX, OUTSOURCED_FILE_NAME_PREFIX, SKIP_PRJ_TYPE_FILE_NAME_PREFIX)):
        dst_files: Set[str] = set()
        ret = deploy_template(file_name, rel_path, "grm.add_file", ini_pdv, dst_files=dst_files)
        if not ret or not dst_files:
            cae.dpo(f"  ### template {file_name} could not be added to {rel_path}")
            return False
        dst_file_name = dst_files.pop()

    else:
        dst_file_name = os.path.join(dst_dir, os.path.basename(file_name))
        if os.path.exists(dst_file_name):
            cae.dpo(f"  ### destination file {dst_file_name} already exists")
            return False
        write_file(dst_file_name, read_file(file_name))

    if not os.path.exists(dst_file_name):                   # pragma: no cover
        cae.dpo(f"  *** failure in adding {dst_file_name} to project {pdv_str(ini_pdv, 'project_desc')}")
        return False

    cae.po(f" ==== added {file_name} to {rel_path} in {pdv_str(ini_pdv, 'project_desc')}")
    return True


@_action()
def bump_version(ini_pdv: PdvType):
    """ increment project version. """
    inc_part = cae.get_option('versionIncrementPart')
    if inc_part not in range(1, 4):
        cae.dpo(f"    = skipped bump of version (because versionIncrementPart=={inc_part})")
        return

    old_version = pdv_str(ini_pdv, 'package_version')
    new_version = increment_version(old_version, increment_part=inc_part)
    nxt_version = next_package_version(ini_pdv, increment_part=inc_part)
    _chk_if(59, new_version == nxt_version,
            f"    * next/incremented package versions out of sync: new-local={new_version} next-remote={nxt_version}")

    bump_file_version(pdv_str(ini_pdv, 'version_file'), increment_part=inc_part)

    ini_pdv.update(project_dev_vars(pdv_str(ini_pdv, 'project_path')))

    cae.po(f" ==== bumped package from version {old_version} to {pdv_str(ini_pdv, 'package_version')}")


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='check')
def check_children_integrity(parent_pdv: PdvType, *children_pdv: PdvType):
    """ run integrity checks for the specified children of a parent or portions of a namespace. """
    for chi_pdv in children_pdv:
        cae.po(f"  --- {pdv_str(chi_pdv, 'package_name')} ---   {pdv_str(chi_pdv, 'project_desc')}")
        check_integrity(chi_pdv)

    cae.po(f"===== passed integrity checks of {_children_desc(parent_pdv, children_pdv)}")


@_action(shortcut='check')
def check_integrity(ini_pdv: PdvType):
    """ integrity check of files/folders completeness, outsourced/template files update-state and CI tests. """
    project_type = pdv_str(ini_pdv, 'project_type')
    if project_type in (NO_PRJ, PARENT_PRJ):
        cae.po(f" ==== no checks for {project_type or 'undefined'} project at {pdv_str(ini_pdv, 'project_path')}")
        return

    _check_folders_files_completeness(ini_pdv)
    if pdv_str(ini_pdv, 'namespace_name') != 'aedev' or 'CI_PROJECT_ID' not in os.environ:
        _check_templates(ini_pdv)   # skip template checks for aedev projects on gitlab CI
    _check_resources(ini_pdv)
    _check_types_linting_tests(ini_pdv)
    cae.po(f" ==== passed integrity checks for {pdv_str(ini_pdv, 'project_desc')}")


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=(('package-versions' + ARG_MULTIPLES,),), pre_action=_check_children_not_exist,
         shortcut='clone')
def clone_children(parent_or_root_pdv: PdvType, *package_versions: str) -> List[str]:
    """ clone specified namespace-portion/parent-child repos to the local machine.

    :param parent_or_root_pdv:  vars of the parent/namespace-root project.
    :param package_versions:    package/project names with optional version of the children to be cloned.
    :return:                    list of project paths of the cloned children projects (for unit testing).
    """
    # _chk_if(15, not cae.get_option('package') and not cae.get_option('path'),
    #         "****  --package and --path options cannot be used with the 'clone-children' action")
    _children_path_package_option_reset()

    project_paths = []
    for pkg_version in package_versions:
        project_paths.append(clone_project(parent_or_root_pdv, pkg_version))

    cae.po(f"===== {len(package_versions)} projects cloned: {package_versions}")
    return project_paths


@_action(ROOT_PRJ, PARENT_PRJ, arg_names=(("--package", ), ("--path", ), ("package-name", ), ("portion-name", )),
         pre_action=_check_children_not_exist, shortcut='clone')
def clone_project(ini_pdv: PdvType, package_or_portion: str = "") -> str:
    """ clone remote repo to the local machine.

    :param ini_pdv:             vars of the project to clone.
    :param package_or_portion:  name of the package/portion to clone, optionally with version number.
    :return:                    project path of the cloned project (used for unit tests).
    """
    parent_path, pkg_and_ver = _get_parent_packageversion(ini_pdv, package_or_portion)

    repo_root = f"{pdv_str(ini_pdv, 'REPO_HOST_PROTOCOL')}{_get_domain(ini_pdv)}/{_get_group(ini_pdv)}"
    package_name, *ver = pkg_and_ver.split(PACKAGE_VERSION_SEP)
    req_branch = cae.get_option('branch')
    branch_or_version = f'v{ver[0]}' if ver else req_branch
    project_path = _git_clone(repo_root, package_name, branch_or_version, parent_path)
    if ver and req_branch:
        _git_checkout(project_dev_vars(project_path=project_path), branch=req_branch)
        pkg_and_ver += f" (branch: {req_branch})"

    cae.po(f" ==== cloned project {pkg_and_ver} from {repo_root} into project path {project_path}")

    return project_path


@_action(PARENT_PRJ, ROOT_PRJ, pre_action=check_children_integrity, shortcut='commit')
def commit_children(ini_pdv: PdvType, *children_pdv: PdvType):
    """ commit changes to children of a namespace/parent using the individually prepared commit message files. """
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'package_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        commit_project(chi_pdv)
    cae.po(f"===== committed {_children_desc(ini_pdv, children_pdv)}")


@_action(pre_action=check_integrity, shortcut='commit')
def commit_project(ini_pdv: PdvType):
    """ commit changes of a single project to the local repo using the prepared commit message file. """
    _git_add(ini_pdv)
    _git_commit(ini_pdv)
    cae.po(f" ==== committed {pdv_str(ini_pdv, 'project_name')}")


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('file-or-folder-name', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def delete_children_file(ini_pdv: PdvType, file_name: str, *children_pdv: PdvType) -> bool:
    """ delete file or empty folder from parent/root and children/portions working trees.

    :param ini_pdv:             parent/root project dev vars.
    :param file_name:           file/folder name to delete (optional with path, relative to working tree root folder).
    :param children_pdv:        tuple of children project dev vars.
    :return:                    True if file got found & deleted from the parent and all children projects, else False.
    """
    c_del = []
    is_root = pdv_str(ini_pdv, 'project_type') == ROOT_PRJ
    if is_root and delete_file(ini_pdv, file_name):
        c_del.append(ini_pdv)

    for chi_pdv in children_pdv:
        if delete_file(chi_pdv, file_name):
            c_del.append(chi_pdv)

    cae.po(f"===== deleted {file_name} in {_children_desc(ini_pdv, children_pdv=c_del)}")
    return len(c_del) == (1 if is_root else 0) + len(children_pdv)


@_action(arg_names=(('file-or-folder-name', ), ))
def delete_file(ini_pdv: PdvType, file_name: str) -> bool:
    """ delete file or empty folder from project working tree.

    :param ini_pdv:             project dev vars.
    :param file_name:           file/folder name to delete (optional with path, relative to working tree root folder).
    :return:                    True if the file got found and delete from the specified project, else False.
    """
    # git is too picky - does not allow deleting unstaged/changed files
    # project_path = pdv_str(ini_pdv, 'project_path')
    # with _in_prj_dir_venv(project_path):
    #     return _cl(89, f"git rm -f {os.path.relpath(file_name, project_path)}", exit_on_err=False) == 0
    file_name = os.path.join(pdv_str(ini_pdv, 'project_path'), file_name)   # prj path ignored if file_name is absolute
    if not os.path.exists(file_name):
        cae.po(f"  *** {file_name} to delete does not exist in {pdv_str(ini_pdv, 'project_desc')}")
        return False

    is_dir = os.path.isdir(file_name)
    if is_dir:
        os.rmdir(file_name)
    else:
        os.remove(file_name)

    if os.path.exists(file_name):               # pragma: no cover
        cae.po(f"  *** error deleting {file_name} from {pdv_str(ini_pdv, 'project_desc')}")
        return False

    cae.po(f" ==== deleted {'folder' if is_dir else 'file'} {file_name} in {pdv_str(ini_pdv, 'project_desc')}")
    return True


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='editable')
def install_children_editable(ini_pdv: PdvType, *children_pdv: PdvType):
    """ install parent children or namespace portions as editable on local machine. """
    for chi_pdv in children_pdv:
        install_editable(chi_pdv)
    cae.po(f"===== installed as editable {_children_desc(ini_pdv, children_pdv)}")


@_action(shortcut='editable')
def install_editable(ini_pdv: PdvType):
    """ install project as editable from source/project root folder. """
    project_path = pdv_str(ini_pdv, 'project_path')
    _cl(90, f"{CMD_INSTALL} -e {project_path}", exit_msg=f"installation from local portions path {project_path} failed")
    cae.po(f" ==== installed as editable: {pdv_str(ini_pdv, 'project_desc')}")


@_action(NO_PRJ, PARENT_PRJ, *ANY_PRJ_TYPE)
def new_app(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a gui app project. """
    return _renew_project(ini_pdv, APP_PRJ)


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='renew')
def new_children(ini_pdv: PdvType, *children_pdv: PdvType) -> List[PdvType]:
    """ initialize or renew parent folder children or namespace portions. """
    _children_path_package_option_reset()
    new_vars = []
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'package_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        new_vars.append(new_project(chi_pdv))
    cae.po(f"===== renewed {_children_desc(ini_pdv, children_pdv=new_vars)}")
    return new_vars


@_action(NO_PRJ, PARENT_PRJ, *ANY_PRJ_TYPE)
def new_django(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew a django project. """
    return _renew_project(ini_pdv, DJANGO_PRJ)


@_action(NO_PRJ, PARENT_PRJ, *ANY_PRJ_TYPE)
def new_module(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew module project. """
    return _renew_project(ini_pdv, MODULE_PRJ)


@_action(NO_PRJ, PARENT_PRJ, *ANY_PRJ_TYPE)
def new_namespace_root(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew namespace root package. """
    return _renew_project(ini_pdv, ROOT_PRJ)


@_action(NO_PRJ, PARENT_PRJ, *ANY_PRJ_TYPE)
def new_package(ini_pdv: PdvType) -> PdvType:
    """ create or complete/renew package project. """
    return _renew_project(ini_pdv, PACKAGE_PRJ)


@_action(shortcut='renew')
def new_project(ini_pdv: PdvType) -> PdvType:
    """ complete/renew an existing project. """
    return _renew_project(ini_pdv, pdv_str(ini_pdv, 'project_type'))


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('commit-message-title', ) + _) for _ in ARGS_CHILDREN_DEFAULT),
         shortcut='prepare')
def prepare_children_commit(ini_pdv: PdvType, title: str, *children_pdv: PdvType):
    """ run code checks and prepare/overwrite the commit message file for a bulk-commit of children projects.

    :param ini_pdv:             parent/root project dev vars.
    :param title:               optional commit message title.
    :param children_pdv:        tuple of project dev vars of the children to process.
    """
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'package_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        prepare_commit(chi_pdv, title=title)
    cae.po(f"===== prepared commit of {_children_desc(ini_pdv, children_pdv)}")


@_action(arg_names=((), ('commit-message-title', ), ), shortcut='prepare')
def prepare_commit(ini_pdv: PdvType, title: str = ""):
    """ run code checks and prepare/overwrite the commit message file for the commit of a single project/package.

    :param ini_pdv:             project dev vars.
    :param title:               optional commit message title.
    """
    _git_add(ini_pdv)
    _write_commit_message(ini_pdv, title=title)
    cae.po(f" ==== prepared commit of {pdv_str(ini_pdv, 'project_desc')}")


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='refresh')
def refresh_children_outsourced(ini_pdv: PdvType, *children_pdv: PdvType):
    """ refresh outsourced files from templates in namespace/project-parent children projects. """
    for chi_pdv in children_pdv:
        cae.po(f" ---  {pdv_str(chi_pdv, 'package_name')}  ---  {pdv_str(chi_pdv, 'project_desc')}")
        refresh_outsourced(chi_pdv)
    cae.po(f"===== refreshed {_children_desc(ini_pdv, children_pdv)}")


@_action(shortcut='refresh')
def refresh_outsourced(ini_pdv: PdvType):
    """ refresh/renew all the outsourced files in the specified project. """
    project_path = pdv_str(ini_pdv, 'project_path')

    dst_files = refresh_templates(ini_pdv, logger=cae.po if cae.get_option('verbose') else cae.vpo)

    dbg_msg = ": " + " ".join(os.path.relpath(_, project_path) for _ in dst_files) if _debug_or_verbose() else ""
    cae.po(f" ==== refreshed {len(dst_files)} outsourced files in {pdv_str(ini_pdv, 'project_desc')}{dbg_msg}")


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('old-name', 'new-name', ) + _) for _ in ARGS_CHILDREN_DEFAULT))
def rename_children_file(ini_pdv: PdvType, old_file_name: str, new_file_name: str, *children_pdv: PdvType) -> bool:
    """ rename file or folder in parent/root and children/portions working trees.

    :param ini_pdv:             parent/root project dev vars.
    :param old_file_name:       file/folder name to rename (optional with path, relative to working tree root folder).
    :param new_file_name:       new name of file/folder (optional with path, relative to working tree root folder).
    :param children_pdv:        tuple of project dev vars of the children to process.
    :return:                    True if the file got renamed in the parent and all children projects, else False.
    """
    ren = []
    if pdv_str(ini_pdv, 'project_type') == ROOT_PRJ and rename_file(ini_pdv, old_file_name, new_file_name):
        ren.append(pdv_str(ini_pdv, 'package_name'))

    for chi_pdv in children_pdv:
        if rename_file(chi_pdv, old_file_name, new_file_name):
            ren.append(pdv_str(chi_pdv, 'package_name'))

    cae.po(f"===== renamed {len(ren)}/{len(children_pdv) + 1} times {old_file_name} to {new_file_name} in: {ren}")
    return len(ren) == 1 + len(children_pdv)


@_action(arg_names=(('old-file-or-folder-name', 'new-file-or-folder-name', ), ))
def rename_file(ini_pdv: PdvType, old_file_name: str, new_file_name: str) -> bool:
    """ rename file or folder in project working tree.

    :param ini_pdv:             project dev vars.
    :param old_file_name:       source file/folder (optional with path, absolute or relative to project working tree).
    :param new_file_name:       destination file/folder (optional path, absolute or relative to project working tree).
    :return:                    True if file/folder got renamed, else False.
    """
    old_file_name = os.path.join(pdv_str(ini_pdv, 'project_path'), old_file_name)   # prj path ignored if absolute
    new_file_name = os.path.join(pdv_str(ini_pdv, 'project_path'), new_file_name)
    if not os.path.exists(old_file_name) or os.path.exists(new_file_name):
        cae.po(f"  ### either source file {old_file_name} not found or destination {new_file_name} already exists")
        return False

    os.rename(old_file_name, new_file_name)     # using os.remove because git mv is too picky

    if os.path.exists(old_file_name) or not os.path.exists(new_file_name):              # pragma: no cover
        cae.po(f"  *** rename of {old_file_name} to {new_file_name} failed: old-exists={os.path.exists(old_file_name)}")
        return False

    cae.po(f" ==== renamed file {old_file_name} to {new_file_name} in {pdv_str(ini_pdv, 'project_desc')}")
    return True


@_action(PARENT_PRJ, ROOT_PRJ, arg_names=tuple(tuple(('command', ) + _) for _ in ARGS_CHILDREN_DEFAULT), shortcut='run')
def run_children_command(ini_pdv: PdvType, command: str, *children_pdv: PdvType):
    """ run console command for the specified portions/children of a namespace/parent.

    :param ini_pdv:             parent/root project dev vars.
    :param command:             console command string (including all command arguments).
    :param children_pdv:        tuple of children project dev vars.
    """
    for chi_pdv in children_pdv:
        cae.po(f"---   {pdv_str(chi_pdv, 'package_name')}   ---   {pdv_str(chi_pdv, 'project_desc')}")

        output: List[str] = []
        with _in_prj_dir_venv(pdv_str(chi_pdv, 'project_path')):
            _cl(98, command, lines_output=output, exit_on_err=not cae.get_option('force'))
        cae.po(_pp(output)[1:])

        if chi_pdv != children_pdv[-1]:
            _wait()

    cae.po(f"===== run command '{command}' for {_children_desc(ini_pdv, children_pdv)}")


@_action(local_action=False, shortcut='actions')    # local_action=False sets remote_repo_api to display remote actions
def show_actions(ini_pdv: PdvType):
    """ get info of available/registered/implemented actions of the specified/current project and remote. """
    compact = not cae.get_option('verbose')
    repo_domain = _get_domain(ini_pdv)
    sep = os.linesep
    ind = " " * 9

    actions = sorted(_available_actions())
    if compact:
        cae.po(f"  --- registered and available actions (locally and on {repo_domain}):")
        for act in actions:
            act_fun = _act_callable(ini_pdv, act)
            if callable(act_fun):
                cae.po(f"    - {act_fun.__name__.replace('_', '-') : <30} {(act_fun.__doc__ or '').split(sep)[0]}")
    else:
        cae.po(f"  --- all registered actions (locally and at {'|'.join(REMOTE_CLASS_NAMES)}):")

        def _act_print(act_reg_key: str):
            spe = REGISTERED_ACTIONS[act_reg_key]
            cae.po(f"{ind}{act_reg_key.replace('_', '-')}==" + (sep + ind).join(_ for _ in spe['docstring'].split(sep)))
            if 'arg_names' in spe:
                cae.po(f"{ind}args: {_expected_args(spe['arg_names'])}")
            cae.po(f"{ind}project types: {', '.join(spe['project_types'])}")
            if 'shortcut' in spe:
                cae.po(f"{ind}shortcut: {spe['shortcut']}")

        for act in actions:
            cae.po(f"    - {act.replace('_', '-')} -------------------------------------------------------------------")
            for name in [act] + [_ + "." + act for _ in REMOTE_CLASS_NAMES.values()]:
                if name in REGISTERED_ACTIONS:
                    _act_print(name)

        cae.po(f"  --- actions registered but not available on {repo_domain}:")
        cae.po(f"      {', '.join(_.replace('_', '-') for _ in actions if not _act_callable(ini_pdv, _)) or '<none>'}")
    cae.po(f" ==== actions available for {pdv_str(ini_pdv, 'project_desc')}")


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='status')
def show_children_status(ini_pdv: PdvType, *children_pdv: PdvType):
    """ run integrity checks for the specified portions/children of a namespace/parent. """
    for chi_pdv in children_pdv:
        show_status(chi_pdv)
    cae.po(f"===== status shown of {_children_desc(ini_pdv, children_pdv)}")


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='versions')
def show_children_versions(ini_pdv: PdvType, *children_pdv: PdvType):
    """ show package versions (local, remote and on pypi) for the specified children of a namespace/parent. """
    for chi_pdv in children_pdv:
        show_versions(chi_pdv)
    cae.po(f"===== versions shown of {_children_desc(ini_pdv, children_pdv)}")


@_action(PARENT_PRJ, *ANY_PRJ_TYPE, shortcut='status')
def show_status(ini_pdv: PdvType):
    """ show git status of the specified/current project and remote. """
    cae.po(f" ---- {pdv_str(ini_pdv, 'package_name')} ---- {pdv_str(ini_pdv, 'project_desc')} project vars:")
    _print_pdv(ini_pdv)

    project_type = pdv_str(ini_pdv, 'project_type')

    if _debug_or_verbose() and project_type in (PARENT_PRJ, ROOT_PRJ):
        presets = _init_children_presets(pdv_val(ini_pdv, 'children_project_vars'))
        cae.po(f"  --- {len(presets)} children presets: ")
        nsp_len = len(pdv_str(ini_pdv, 'namespace_name'))
        if nsp_len:
            nsp_len += 1
        for preset, dep_packages in presets.items():
            cae.po(f"      {preset: <9} == {', '.join(pkg[nsp_len:] for pkg in sorted(dep_packages))}")

    if project_type not in (NO_PRJ, PARENT_PRJ):
        project_path = pdv_str(ini_pdv, 'project_path')

        cur_branch = _git_current_branch(ini_pdv)
        if cur_branch != MAIN_BRANCH:
            cae.po(f"   -- current working branch of project at '{project_path}' is '{cur_branch}'")
            cae.po(f"  --- git diff {cur_branch} against {MAIN_BRANCH} branch:{_pp(_git_diff(ini_pdv, MAIN_BRANCH))}")

        cae.po(f"  --- git diff - to be staged/added:{_pp(_git_diff(ini_pdv))}")

        cae.po(f"  --- git diff {MAIN_BRANCH} origin/{MAIN_BRANCH} (run 'grm update' to update local {MAIN_BRANCH}):"
               f"{_pp(_git_diff(ini_pdv, MAIN_BRANCH, f'origin/{MAIN_BRANCH}'))}")

        cae.po(f"  --- git status:{_pp(_git_status(ini_pdv))}")

        cae.po(f"  --- branches:{_pp(_git_branches(ini_pdv))}")
        cae.po(f"  --- remotes:{_pp(f'{name}={url}' for name, url in _git_remotes(ini_pdv).items())}")

        changed = _git_uncommitted(ini_pdv)
        if changed:
            cae.po(f"   -- '{project_path}' has {len(changed)} uncommitted files: {changed}")
    cae.po(f" ==== status shown of {pdv_str(ini_pdv, 'project_desc')}")


@_action(shortcut='versions')
def show_versions(ini_pdv: PdvType):
    """ display package versions of local, remote and latest published onto PyPI. """
    _git_fetch(ini_pdv)
    loc = pdv_str(ini_pdv, 'package_version')
    rem = _git_tag_list(ini_pdv)
    pyp = pypi_versions(pdv_str(ini_pdv, 'package_name'))
    cae.po(f" ==== {pdv_str(ini_pdv, 'package_name'): <27}local:{loc: <9} remote:{rem[-1][1:]: <9} pypi:{pyp[-1]: <9}")


@_action(PARENT_PRJ, ROOT_PRJ, shortcut='update')
def update_children(ini_pdv: PdvType, *children_pdv: PdvType):
    """ fetch and rebase the MAIN_BRANCH to the local children repos of the parent/namespace-root(also updated). """
    for chi_pdv in children_pdv:
        update_project(chi_pdv)
    cae.po(f"===== updated {_children_desc(ini_pdv, children_pdv)}")


@_action(shortcut='update')
def update_project(ini_pdv: PdvType) -> List[str]:
    """ fetch and rebase the MAIN_BRANCH of the specified project in the local repo. """
    with _in_prj_dir_venv(pdv_str(ini_pdv, 'project_path')):
        sh_err = _cl(33, f"git branch --set-upstream-to origin/{MAIN_BRANCH} {MAIN_BRANCH}", exit_on_err=False)
        if sh_err and _debug_or_verbose():
            cae.po(f"    # ignoring error {sh_err} renewing tracking of main branch {MAIN_BRANCH}")

    errors = _git_fetch(ini_pdv)
    if errors and _debug_or_verbose():
        cae.po(f" #### update_project cannot update local branch because of 'git fetch' errors:{_pp(errors)}")
    else:
        _git_fetch(ini_pdv, ".", f"origin/{MAIN_BRANCH}:{MAIN_BRANCH}")

    cae.po(f" ==== updated {pdv_str(ini_pdv, 'project_desc')}")
    return errors


# ----------------------- main ----------------------------------------------------------------------------------------


def main():                                                                                 # pragma: no cover
    """ main app script """
    cae.add_argument('action', help="action to execute (run `grm -v show-actions` to display all available actions)")
    cae.add_argument('arguments',
                     help="additional arguments, depending on specified action, e.g. all children actions expecting"
                          " either a list of package/portion names or an expression using one of the preset children"
                          " sets like all|editable|modified|develop|filterBranch|filterExpression",
                     nargs='*')
    cae.add_option('branch', "branch or version-tag to checkout/filter-/work-on", "")
    cae.add_option('delay', "seconds to pause, e.g. between sub-actions of a children-bulk-action", 69, short_opt='w')
    cae.add_option('domain', "repository remote host domain of project (gitlab.com|github.com|...)", "")
    cae.add_option('force', "force execution of action, ignoring minor errors", UNSET)
    cae.add_option('filterExpression', "Python expression evaluated against each children project, to be used as"
                                       " 'filterExpression' children-set-expression argument", "", short_opt='F')
    cae.add_option('filterBranch', "branch name matching the children current branch, to be used as"
                                   " 'filterBranch' children-set-expression argument", "", short_opt='B')
    cae.add_option('gitToken', "personal/private access token to connect to remote host", "", short_opt='t')
    cae.add_option('gitUser', "user name on to remote host (used for upstream/fork url)", "", short_opt='u')
    cae.add_option('group', "group or user name of a new project repository at the remote host", "")
    cae.add_option('namespace', "namespace name for new namespace root or portion (module/package) project", "")
    cae.add_option('package', "package, project or portion name", "", short_opt='k')
    cae.add_option('path', "project directory of a new (namespace) package (default=current working directory)", "")
    cae.add_option('verbose', "verbose console output", UNSET)
    cae.add_option('versionIncrementPart', "project version number part to increment (0=disable, 1...3=mayor...patch)",
                   3, short_opt='i', choices=range(4))
    for import_name in TPL_PACKAGES:
        cae.add_option(_template_version_option(import_name),
                       f"branch/version-tag of {import_name} template package (default=latest version)",
                       "",
                       short_opt=UNSET)
    cae.run_app()                                           # parse command line arguments

    ini_pdv, act_name, act_args = _init_act_exec_args()     # init globals, check if action is implemented, compile args
    _act_callable(ini_pdv, act_name)(ini_pdv, *act_args)    # execute action

    if TEMP_CONTEXT:
        TEMP_CONTEXT.cleanup()


if __name__ == '__main__':                                                                      # pragma: no cover
    try:
        main()
    except Exception as main_ex:
        debug_info = f":{os.linesep}{format_exc()}" if _debug_or_verbose() else ""
        _exit_error(99, f"***** unexpected exception {main_ex} raised{debug_info}")
