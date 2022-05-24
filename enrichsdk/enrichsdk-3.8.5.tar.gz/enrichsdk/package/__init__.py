"""
Enrich Platform module packaging service.

This service allows you to boostrap (create a new module) and unit
test it before uploading to the server.

"""

import os
import sys
import json
import stat
import warnings
import imp
import copy
import glob2
import shutil
import importlib
import importlib.util
import traceback
import inspect
import logging
from datetime import datetime, date, timezone, timedelta
from time import gmtime, strftime
from collections import OrderedDict, defaultdict

import pytz
from tzlocal import get_localzone
from dateutil import parser as dateparser

from enrichsdk.tasks import Task
from enrichsdk.tasks.sdk import *
from prompt_toolkit import prompt

try:
    from prompt_toolkit.contrib.completers import WordCompleter
except:
    from prompt_toolkit.completion import WordCompleter

from .validators import *
from .lib import *
from .log import setup_logging
from .mock import *
from ..lib import *
from ..lib.customer import load_customer_assets
from ..app.flask.render import create_app
from enrichsdk.tasks import Task
from enrichsdk.core.res import set_limits

__all__ = [
    "bootstrap",
    "test_transform",
    "test_conf",
    "test_task",
    "checkenv",
    "print_log",
    "testdata_action",
    "get_sample_siteconf",
    "get_sample_versionmap",
    "populate",
]


class DataFilter(logging.Filter):
    def filter(self, record):

        data = getattr(record, "data", "")
        if isinstance(data, str) and len(data) > 0:
            data = "\n" + data
        record.data = data

        transform = getattr(record, "transform", "")
        record.transform = transform

        return True


# Insert the filter for app messages
logger = logging.getLogger("app")
df = DataFilter()
logger.addFilter(df)
for name in [
    "kazoo.client",
    "pykafka.simpleconsumer",
    "pykafka.handlers",
    "pykafka.balancedconsumer",
    "pykafka.connection",
    "pykafka.membershipprotocol",
    "pykafka.cluster",
    "pykafka.topic",
]:
    logging.getLogger(name).disabled = True


#################################################
# Helper
#################################################
def welcome():
    print("==============================")
    print("  Welcome to Scribble Enrich ")
    print("=============================")
    print("\n")


def read_conf():

    # Created a global configuration
    confpath = "enrich.json"
    if os.path.exists(confpath):
        try:
            conf = json.loads(open(confpath).read())
            assert "org" in conf
            assert "repository" in conf
            return conf
        except:
            traceback.print_exc()
            pass

    print(
        "First we have to create a configuration file (enrich.json). After we update you"
    )
    print("will find the content in {}".format(confpath))

    msg = """\nPlease enter your customer organization details.

Note that the organization name has to be precise. Please check with
Scribble if you are not sure\n"""
    print(msg)

    validators = OrderedDict()
    defaults = {"name": os.path.basename(os.path.abspath("."))}

    validators["name"] = NameValidator()
    validators["description"] = OrgDescValidator()
    validators["logourl"] = LogoValidator()

    orgcontext = {}
    for v in validators:
        orgcontext[v] = prompt(
            "> " + v + ": ",
            default=defaults.get(v, ""),
            validator=validators.get(v, None),
        )

    msg = (
        """\nThanks! \n\nNow, please enter your and details of this code repository\n"""
    )
    print(msg)

    validators = OrderedDict()
    validators["name"] = NameValidator()
    validators["email"] = EmailValidator()
    validators["giturl"] = URLValidator()

    devcontext = {}
    for v in validators:
        devcontext[v] = prompt("> " + v + ": ", validator=validators.get(v, None))

    devcontext["author"] = devcontext.pop("name")

    context = orgcontext
    context.update(devcontext)

    # Get the template
    template = get_template_path("enrich.json.template")

    # Write a local copy
    content = write_rendered_file(template, ".", "enrich.json", context)

    # Write a global enrich.json as well
    content = write_rendered_file(
        template, os.environ["ENRICH_ETC"], "enrich.json", context
    )

    print("Wrote global configuration file {}".format(confpath))

    return json.loads(content)


############################################################
# Prepare workspace
############################################################
def prepare_enrich_root(target):
    for d in ["data", "etc", "customers"]:
        try:
            os.makedirs(os.path.join(target, d))
        except:
            pass


############################################################
# Prepare repo
############################################################
def prepare_repo(target):

    # First create init file
    template = get_template_path("repo.init.template")
    write_rendered_file(template, target, "__init__.py", {})
    print(greenbg("Wrote __init__.py in {}".format(target)))

    # Load if one already exists..
    try:
        defaults = load_enrichjson_defaults(target, usecase=False)
    except:
        traceback.print_exc()
        defaults = {}

    prepare_enrichjson(target, defaults=defaults, template="root.enrich.json.template")
    print(greenbg("Wrote enrich.json in {}".format(target)))

    defaults = load_enrichjson_defaults(target, usecase=False)

    msg = (
        """\
[%(org_name)s] Code Repository
--------

Enrich modules for various usecases"""
        % defaults
    )
    readme = os.path.join(target, "README.rst")
    if not os.path.exists(readme):
        with open(readme, "w") as fd:
            fd.write(msg)
    print(greenbg("Added a README.rst in {}".format(target)))

    requirements = os.path.join(target, "requirements.txt")
    if not os.path.exists(requirements):
        with open(requirements, "w") as fd:
            fd.write("#")
    print(greenbg("Added a requirements.txt in {}".format(target)))


############################################################
# Prepare workspace
############################################################
def load_enrichjson_defaults(target, usecase=True):

    defaults = {}

    if usecase:
        enrichjsons = glob2.glob(target + "/../*/enrich.json") + glob2.glob(
            target + "/../*enrich.json"
        )
    else:
        enrichjsons = glob2.glob(target + "/*enrich.json")

        # Initialize
        defaults["org_name"] = os.path.basename(os.path.abspath(target))
        defaults["usecase_name"] = "Unknown"

    for enrichjson in enrichjsons:
        try:
            j = json.load(open(enrichjson))
            defaults["org_name"] = j["org"]["customer"]
            defaults["org_logourl"] = j["org"]["logo"]
            defaults["org_description"] = j["org"]["description"]
            defaults["author_name"] = j["repository"]["author"]
            defaults["author_email"] = j["repository"]["email"]
            defaults["repo_giturl"] = j["repository"]["giturl"]
        except:
            pass

    return defaults


def prepare_workspace(target, force=False, auto=False):
    if "/" in target and not force:
        raise Exception("Only sub-directory name should be mentioned without /")

    usecasename = os.path.basename(target)
    customer = os.path.basename(os.path.dirname(target))

    parentenrich = os.path.join(customer, "enrich.json")
    if not os.path.exists(parentenrich):
        raise Exception("enrich.json missing in root directory")

    for d in [
        "pipelines",
        "pipelines/conf",
        "pipelines/lib",
        "pipelines/jobs",
        "dashboard",
        "bin",
        "docs",
        "commands",
        "transforms",
        "assets",
        "tasks",
        "tasks/conf",
        "tasks/lib",
        "tasks/jobs",
        "workflows",
        "workflows/prefect",
        "workflows/spark",
    ]:
        path = os.path.join(target, d)
        try:
            os.makedirs(path)
        except:
            pass
        print("Created {}".format(path))

    try:
        data_root = os.path.join(os.environ["ENRICH_TEST"], usecasename)
        if not os.path.exists(data_root):
            os.makedirs(data_root)
            print("Created data_root in {}".format(data_root))

    except:
        traceback.print_exc()

    msg = """\
[{0}] {1}
--------

Enrich modules for {1}""".format(
        customer, usecasename
    )
    readme = os.path.join(target, "README.rst")
    if not os.path.exists(readme):
        with open(readme, "w") as fd:
            fd.write(msg)
    print("Added a readme in {}".format(readme))

    defaults = load_enrichjson_defaults(target, usecase=True)

    prepare_enrichjson(target, defaults, auto)


def prepare_enrichjson(target, defaults, auto=False, template="enrich.json.template"):

    print("Preparing enrich.json metadata file")

    enrichjson = "enrich.json"
    filename = os.path.join(target, enrichjson)

    # Get the template
    template = get_template_path(template)

    variables = get_variables(template)

    validators = {}
    validators["usecase_name"] = NameValidator()

    context = {}
    if not auto:
        for v in variables:
            context[v] = prompt(
                "> " + v + ": ",
                default=defaults.get(v, ""),
                validator=validators.get(v, None),
            )
    else:
        for v in variables:
            context[v] = defaults.get(v, "unspecified")

    # Write a local copy
    write_rendered_file(template, target, "enrich.json", context)


############################################################
# Convert
############################################################
def prepare_setup(component, target):

    if os.path.exists(target):
        raise Exception("Destination exists. Please remove it.")

    conf = read_conf()

    basename = os.path.basename(target)
    repo = conf.get("repository", {})
    org = conf.get("org", {})
    params = {
        "component": component,
        "basename": basename,
        "name": basename,
        "version": "0.1",
        "description": basename + " package",
        "author": repo.get("author", ""),
        "email": repo.get("email", ""),
        "url": repo.get("giturl", ""),
        "customer": org.get("name", ""),
    }

    # => Write the manifest file
    # Write the manifest file...
    write_rendered_file("MANIFEST.in.template", target, "MANIFEST.in", params)
    write_rendered_file("setup.cfg.template", target, "setup.cfg", params)
    write_rendered_file("LICENSE.template", target, "LICENSE", params)
    write_rendered_file("setup.py.template", target, "setup.py", params)

    testdir = os.path.join(target, "tests")
    try:
        os.makedirs(testdir)
    except:
        pass

    write_rendered_file("test_module.py.template", testdir, "test_module.py", params)

    # Copy the fixtures
    src = os.path.join(default_templatedir, "fixtures")
    dst = os.path.join(testdir, "fixtures")
    shutil.copytree(src, dst)

    with open(os.path.join(testdir, "__init__.py"), "w") as fd:
        fd.write("")

    print(greenbg("Created a package in {}".format(target)))
    print(
        redbg(
            "Note: Please look at fixtures in tests/fixtures and update the paths for data_root and statedir"
        )
    )


def prepare_dashboard(target, templatepath):
    """
    Bootstrap a dashboard
    """

    appname = os.path.basename(target)
    appdesc = prompt("app description>")

    templatedir = os.path.join(target, "templates", appname)
    try:
        os.makedirs(target)
        os.makedirs(templatedir)
    except:
        pass

    dashboard_root = get_template_path("dashboard")

    # First copy the py files
    files = glob2.glob(dashboard_root + "/*py")
    for f in files:
        content = open(f).read()
        content = content.replace("APPNAME", appname)
        content = content.replace("APPDESC", appdesc)
        basename = os.path.basename(f)
        targetfile = os.path.join(target, basename)
        with open(targetfile, "w") as fd:
            fd.write(content)
        print(basename, "=>", targetfile)

    # Now copy the html files...
    files = glob2.glob(os.path.join(dashboard_root, "templates", "*html"))
    print(files)
    for f in files:
        content = open(f).read()
        content = content.replace("APPNAME", appname)
        basename = os.path.basename(f)
        targetfile = os.path.join(templatedir, basename)
        with open(targetfile, "w") as fd:
            fd.write(content)
        print(basename, "=>", targetfile)

    print("Add the following to the enrich.json")
    print(
        json.dumps(
            {
                "installed_apps": [
                    f"{appname}.apps.{appname}Config"
                ]
            },
            indent=4,
        )
    )


def prepare_asset(what, target, templatepath):

    print("Bootstrapping a {}".format(what))
    if what not in ["asset"]:
        raise Exception("Unsupported component")

    if templatepath is not None:
        raise Exception("Asset template not supported yet")

    if os.path.exists(target):
        raise Exception("Target directory exists. Please remove it")

    conf = read_conf()

    # Create setup.py etc.
    prepare_setup(what, target)

    content = '''\
#!/usr/bin/env python
# coding: utf-8
"""
    A description which can be long and explain the complete
    functionality of this module even with indented code examples.
    Class/Function however should not be documented here. They can
    go into the individual functions.

"""
    '''

    # Initialize the library...
    libname = os.path.basename(target)
    initfile = os.path.join(target, "src", libname, "__init__.py")
    try:
        os.makedirs(os.path.dirname(initfile))
    except:
        pass
    with open(initfile, "w") as fd:
        fd.write(content)

    s3root = prompt("s3root>")
    servername = prompt("servername>")

    asset_root = get_template_path("assets")
    files = glob2.glob(asset_root + "/*py")
    for f in files:
        content = open(f).read()
        content = content.replace("S3ROOT", s3root)
        content = content.replace("SERVERNAME", servername)
        basename = os.path.basename(f)
        targetfile = os.path.join(target, "src", libname, basename)
        with open(targetfile, "w") as fd:
            fd.write(content)
        print(basename, "=>", targetfile)

    # Bye bye
    print("Bootstrapped asset library {}".format(target))


def prepare_component(what, target, templatepath):

    print("Bootstrapping a {}".format(what))
    if what not in ["transform-package"]:
        raise Exception("Unsupported component")

    if os.path.exists(target):
        raise Exception("Target directory exists. Please remove it")

    conf = read_conf()

    # Create setup.py etc.
    prepare_setup(what, target)

    # => Load the manifest
    print("Please provide component details:")
    defaults = {
        "version": "1.0",
        "minorversion": "1.0",
        "author_name": conf.get("repository", {}).get("author", "John Smith"),
        "author_email": conf.get("repository", {}).get(
            "email", "john.smith@alphainc.com"
        ),
        "repo_giturl": conf.get("repository", {}).get(
            "giturl", "git@github.com:alpha/enrich-alpha.git"
        ),
        "org_logourl": conf.get("org", {}).get(
            "logo", "https://alphainc.com/logo/small.png"
        ),
        "org_name": conf.get("org", {}).get("name", "Alpha Inc"),
        "org_description": conf.get("description", {}).get("name", "Alpha retail"),
    }

    validators = {
        "name": NameValidator(),
        "transform_name": NameValidator(),
        "description": GenericDescValidator(),
        "transform_description": GenericDescValidator(),
    }

    manifestfile = get_template_path("manifest.json.template")
    context = {}
    variables = get_variables(manifestfile)
    for v in variables:
        context[v] = prompt(
            "> " + v + ": ",
            default=defaults.get(v, ""),
            validator=validators.get(v, None),
        )

    dst = os.path.join(target, os.path.basename(target))
    write_rendered_file(manifestfile, dst, "manifest.json", context)
    write_rendered_file("README.md.template", dst, "README.md", context)

    # Get the right template
    if templatepath is None:
        templates = list_templates(suffix=".node.template")
        templatepath = templates["transform"]
        # templatepath = 'transform.node.template'
        # template_completer = WordCompleter(list(templates.keys()),
        #                                   ignore_case=True)
        # name = prompt('> Type of Transform: ',
        #              default=list(templates.keys())[0],
        #              completer=template_completer)
        # templatepath = templates[name]

    variables = get_variables(templatepath)
    for v in variables:
        if v not in context:
            context[v] = prompt(
                "> " + v + ": ",
                default=defaults.get(v, ""),
                validator=validators.get(v, None),
            )
    write_rendered_file(templatepath, dst, "__init__.py", context)

    # Bye bye
    print("Bootstrapped {} {} in {}".format(what, context["transform_name"], target))


def prepare_config(path, templatepath):

    welcome()

    print("Bootstrapping a new configuration\n")

    conf = read_conf()

    validators = {"name": NameValidator(), "description": GenericDescValidator()}

    print("\nPlease provide configuration details\n")
    if templatepath is None:
        config_template = get_template_path("config.json.template")
    else:
        config_template = templatepath

    context = {}
    variables = get_variables(config_template)
    for v in variables:
        context[v] = prompt("> " + v + ": ", validator=validators.get(v, None))
    config = render(config_template, context)

    with open(path, "w") as fd:
        fd.write(config)

    # Bye bye
    print("Bootstrapped configuration {} in {}".format(context["name"], path))


def prepare_tasklib(path, templatepath):

    welcome()

    print("Bootstrapping a new task library\n")

    conf = read_conf()

    validators = {"name": NameValidator(), "description": GenericDescValidator()}

    print("\nPlease provide configuration details\n")
    if templatepath is None:
        lib_template = get_template_path("tasklib.template")
    else:
        lib_template = templatepath

    context = {}
    variables = get_variables(lib_template)
    for v in variables:
        context[v] = prompt("> " + v + ": ", validator=validators.get(v, None))
    content = render(lib_template, context)

    try:
        os.makedirs(path)
    except:
        pass

    initfile = os.path.join(path, "__init__.py")
    with open(initfile, "w") as fd:
        fd.write(content)

    # Bye bye
    print("Bootstrapped configuration {} in {}".format(context["name"], path))


def prepare_taskconf(path, templatepath):

    welcome()

    print("Bootstrapping a new task configuration file\n")

    conf = read_conf()

    if not path.lower().endswith(".json"):
        print("Task configuration file should be a json")
        return

    validators = {
        "taskdag_name": NameValidator(),
        "taskdag_name": NameValidator(),
        "runid_prefix": NameValidator(),
        "task_name": NameValidator(),
        "description": GenericDescValidator(),
    }

    print("\nPlease provide configuration details\n")
    if templatepath is None:
        lib_template = get_template_path("taskconf.template")
    else:
        lib_template = templatepath

    defaults = {
        "customer": conf["org"]["customer"],
        "usecase": conf["org"]["name"],
    }

    context = {}
    variables = get_variables(lib_template)
    for v in variables:
        context[v] = prompt(
            "> " + v + ": ",
            default=defaults.get(v, ""),
            validator=validators.get(v, None),
        )
    content = render(lib_template, context)

    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    with open(path, "w") as fd:
        fd.write(content)

    # Bye bye
    print("Bootstrapped configuration {} in {}".format(context["taskdag_name"], path))


def prepare_pipelineconf(path, templatepath):

    welcome()

    print("Bootstrapping a new pipeline configuration file\n")

    conf = read_conf()

    if not (path.lower().endswith(".json") or path.lower().endswith(".py")):
        print("Pipeline configuration file should be a json")
        return

    validators = {
        "pipeline_name": NameValidator(),
        "pipeline_description": GenericDescValidator(),
        "usecase": NameValidator(),
        "runid_prefix": NameValidator(),
        "notification_email": EmailValidator(),
        "transform": NameValidator(),
        "realtime_or_batch": RealtimeBatchValidator(),
    }

    print("\nPlease provide configuration details\n")

    if templatepath is None:
        if path.lower().endswith(".py"):
            lib_template = get_template_path("pipelinepyconf.template")
        else:
            lib_template = get_template_path("pipelineconf.template")
    else:
        lib_template = templatepath

    defaults = {
        "realtime_or_batch": "batch",
        "customer": conf.get("org", {}).get("customer", ""),
        "usecase": conf.get("org", {}).get("name", ""),
    }

    context = {}
    variables = get_variables(lib_template)
    for v in variables:
        context[v] = prompt(
            "> " + v + ": ",
            default=defaults.get(v, ""),
            validator=validators.get(v, None),
        )

    content = render(lib_template, context)

    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    with open(path, "w") as fd:
        fd.write(content)

    # Bye bye
    print("Bootstrapped pipeline specification in {}".format(path))


def prepare_script_default(path, templatepath):

    if os.path.exists(path):
        raise Exception("Output path already exists. Please remove it")

    conf = read_conf()

    validators = {
        "confname": NameValidator(),
        "runname": NameValidator(),
        "email": EmailValidator(),
        "transform": NameValidator(),
        "description": GenericDescValidator(),
    }

    context = {
        "today": date.today().isoformat(),
        "author_email": conf["repository"]["email"],
        "email": conf["repository"]["email"],
        "author": conf["repository"]["author"],
        "customer": conf["org"]["customer"],
        "division": conf["org"]["name"],
    }
    variables = get_variables(templatepath)
    for v in variables:
        context[v] = prompt(
            "> " + v + ": ",
            default=context.get(v, ""),
            validator=validators.get(v, None),
        )

    content = render(templatepath, context)

    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    with open(path, "w") as fd:
        fd.write(content)

    # Bye bye
    print("Bootstrapped script in {}".format(path))


def prepare_script_minimal(path, templatepath):

    if os.path.exists(path):
        raise Exception("Output path already exists. Please remove it")

    try:
        conf = read_conf()
    except:
        conf = {}

    validators = {
        "confname": NameValidator(),
        "runname": NameValidator(),
        "email": EmailValidator(),
        "transform": NameValidator(),
        "description": GenericDescValidator(),
    }

    context = {
        "today": date.today().isoformat(),
        "author_name": conf.get("repository", {}).get("author", "John Smith"),
        "author_email": conf.get("repository", {}).get(
            "email", "john.smith@alphainc.com"
        ),
        "repo_giturl": conf.get("repository", {}).get(
            "giturl", "git@github.com:alpha/enrich-alpha.git"
        ),
        "org_logourl": conf.get("org", {}).get(
            "logo", "https://alphainc.com/logo/small.png"
        ),
        "org_name": conf.get("org", {}).get("name", "Alpha Inc"),
        "org_description": conf.get("description", {}).get("name", "Alpha retail"),
    }

    variables = get_variables(templatepath)
    for v in variables:
        context[v] = prompt(
            "> " + v + ": ",
            default=context.get(v, ""),
            validator=validators.get(v, None),
        )

    content = render(templatepath, context)

    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass

    with open(path, "w") as fd:
        fd.write(content)

    # Bye bye
    print("Bootstrapped script in {}".format(path))


def prepare_rscript(path, templatepath):

    welcome()

    print("Bootstrapping an R Script\n")

    if not path.lower().endswith(".r"):
        print("R script should end with .r/R")
        return

    if templatepath is None:
        lib_template = get_template_path("rscript.template")
    else:
        lib_template = templatepath

    prepare_script_default(path, lib_template)


def prepare_pyscript(path, templatepath):

    welcome()

    print("Bootstrapping an Python Script\n")

    if not path.lower().endswith(".py"):
        print("py script should end with .py")
        return

    if templatepath is None:
        lib_template = get_template_path("pyscript.template")
    else:
        lib_template = templatepath

    prepare_script_default(path, lib_template)


def prepare_transform_script(path, templatepath, what="simpletransform"):

    welcome()

    print("Bootstrapping a simple transform\n")

    path = path.strip()
    if not path.endswith(".py"):
        path = path + "/__init__.py"

    if templatepath is None:
        lib_template = get_template_path(what + ".node.template")
    else:
        lib_template = templatepath

    prepare_script_minimal(path, lib_template)


def prepare_sparkjob(path, templatepath):
    """
    Bootstrap a new sparkjob

    Parameters
    ----------
    component: Nature of the module that should be bootstrapped
    path: Path where the module should be created.

    Yields
    ------
    directory hierarchy

    """
    if templatepath is not None:
        raise Exception("sparkjob template not supported yet")

    src = os.path.join(default_templatedir, "spark")
    dst = path
    if os.path.exists(dst):
        raise Exception("Destination exists. Please remove it")

    shutil.copytree(src, dst)

    # Bye bye
    print("Bootstrapped sparkjob")


def prepare_airflowjob(path, templatepath):
    """
    Bootstrap a new airflowjob

    Parameters
    ----------
    component: Nature of the module that should be bootstrapped
    path: Path where the module should be created.

    Yields
    ------
    directory hierarchy

    """

    if templatepath is not None:
        raise Exception("airflowjob template not supported yet")

    src = os.path.join(default_templatedir, "airflow", "contrib-pipeline-v1.py")
    dst = path
    if os.path.exists(dst):
        raise Exception("Destination exists. Please remove it")

    shutil.copy(src, dst)

    # Bye bye
    print("Bootstrapped airflowjob")


def prepare_prefectjob(path, templatepath):
    """
    Bootstrap a new prefect

    Parameters
    ----------
    component: Nature of the module that should be bootstrapped
    path: Path where the module should be created.

    Yields
    ------
    directory hierarchy

    """

    if templatepath is not None:
        raise Exception("prefectjob template not supported yet")

    src = os.path.join(default_templatedir, "prefect", "default.py")
    dst = path
    if os.path.exists(dst):
        raise Exception("Destination exists. Please remove it")

    shutil.copy(src, dst)

    # Update the execute permissions
    st = os.stat(dst)
    os.chmod(dst, st.st_mode | stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR)

    # Bye bye
    print("Bootstrapped prefectjob")


def bootstrap(component, path, templatepath):
    """
    Bootstrap a new module (python package)

    Currently transform and model are supported modules

    Parameters
    ----------
    component: Nature of the module that should be bootstrapped
    path: Path where the module should be created.

    Yields
    ------
    A python package

    """

    if False:
        if "ENRICH_ROOT" not in os.environ:
            print(
                "ENRICH_ROOT variable not defined. Looks like you haven't source enrich-env.sh"
            )
            raise Exception("Environment missing: Please define ENRICH_ROOT")

    path = path.rstrip("/")  # For the case when user has added a trailing '/'

    if component == "transform-package":
        prepare_component("transform-package", path, templatepath)
    elif component in ["transform-simple"]:
        prepare_transform_script(path, templatepath, what="simpletransform")
    elif component in ["transform-helloworld"]:
        prepare_transform_script(path, templatepath, what="helloworld")
    elif component in ["transform-query"]:
        prepare_transform_script(path, templatepath, what="query")
    elif component in ["transform-iris"]:
        prepare_transform_script(path, templatepath, what="iris")
    # elif component == 'model':
    #    prepare_component('model', path, templatepath)
    # elif component == 'skin':
    #    prepare_component('skin', path, templatepath)
    elif component == "config":
        prepare_config(path, templatepath)
    elif component == "repo":
        prepare_repo(path)
    elif component == "asset":
        prepare_asset("asset", path, templatepath)
    elif component == "dashboard":
        prepare_dashboard(path, templatepath)
    elif component in ["tasklib", "task-lib"]:
        prepare_tasklib(path, templatepath)
    elif component in ["taskconf", "task-conf"]:
        prepare_taskconf(path, templatepath)
    elif component in ["pipelineconf", "pipeline-conf"]:
        prepare_pipelineconf(path, templatepath)
    elif component in ["workspace", "usecase"]:
        prepare_workspace(path)
    elif component in ["sparkjob", "spark", "spark-job"]:
        prepare_sparkjob(path, templatepath)
    elif component in ["airflowjob", "airflow"]:
        prepare_airflowjob(path, templatepath)
    elif component in ["prefect", "prefectjob"]:
        prepare_prefectjob(path, templatepath)
    elif component in ["rscript"]:
        prepare_rscript(path, templatepath)
    elif component in ["pyscript"]:
        prepare_pyscript(path, templatepath)


def get_sample_siteconf():
    siteconf = """\
{
    "customer": "Acme Inc",
    "dashboard": {
        "title": "Acme Rich Data Platform"
    },
    "credentials": {
        "data-bucket": {
            "nature": "s3",
            "bucket": "acme-datalake",
            "readonly": false,
            "access_key": "AKIAJURXL...Q",
            "secret_key": "tutww...A"
        }
    }
}\
    """
    return siteconf


def get_sample_versionmap():
    versionmap = """\
[
    {
    "description": "Enrich SDK for pipeline development",
    "date": "2018-03-20 16:14:19 +0530",
    "repo": "enrich-sdk",
    "release": "v1.5.5",
    "label": "sdk",
    "commit": "6b406f0b083b962c164ac54431a44811c45b9ff0"
    }
]\
    """
    return versionmap


def populate(context={}):
    """
    Creates the enrich working space
    """
    variables = [
        "ENRICH_ROOT",
        "ENRICH_DATA",
        "ENRICH_TEST",
        "ENRICH_ETC",
        "ENRICH_SHARED",
        "ENRICH_VAR",
        "ENRICH_LIB",
        "ENRICH_OPT",
        "ENRICH_LOGS",
        "ENRICH_CUSTOMERS",
        "ENRICH_RELEASES",
        "ENRICH_TEST",
    ]
    for var in variables:
        if var in os.environ:
            path = os.environ[var]
            try:
                if os.path.exists(path):
                    print(orangebg(var + " exists"))
                else:
                    os.makedirs(path)
                    print(greenbg(var + " created"))
            except:
                pass

    siteconf = None
    if "siteconf" in os.environ:
        siteconf = os.environ["siteconf"]
    elif "siteconf" in context:
        siteconf = context["siteconf"]
    elif "ENRICH_ETC" in os.environ:
        siteconf = os.path.join(os.environ["ENRICH_ETC"], "siteconf.json")
    else:
        print(redbg("Path for siteconf not found"))

    if siteconf is not None:
        if os.path.exists(siteconf):
            print(orangebg("siteconf already present"))
        else:
            try:
                with open(siteconf, "w") as fd:
                    fd.write(get_sample_siteconf())
                print(greenbg("siteconf initialized"))
            except:
                print(redbg("siteconf could not be created"))

    # => Versionmap
    versionmap = None
    if "versionmap" in os.environ:
        versionmap = os.environ["versionmap"]
    elif "versionmap" in context:
        versionmap = context["versionmap"]
    elif "ENRICH_ETC" in os.environ:
        versionmap = os.path.join(os.environ["ENRICH_ETC"], "versionmap.json")
    else:
        print(redbg("Path for versionmap not found"))

    if versionmap is not None:
        if os.path.exists(versionmap):
            print(orangebg("versionmap already present"))
        else:
            try:
                with open(versionmap, "w") as fd:
                    fd.write(get_sample_versionmap())
                print(greenbg("versionmap initialized"))
            except:
                print(redbg("versionmap could not be created"))

    if "ENRICH_CUSTOMERS" in os.environ and "ENRICH_DATA" in os.environ:
        enrich_customers = os.environ["ENRICH_CUSTOMERS"]
        enrich_data = os.environ["ENRICH_DATA"]
        if os.path.exists(enrich_customers):
            customers = os.listdir(enrich_customers)
            if len(customers) == 0:
                print(
                    redbg(
                        "No applications linked in ENRICH_CUSTOMERS {}".format(
                            enrich_customers
                        )
                    )
                )
            else:
                for c in customers:
                    for usecase in os.listdir(os.path.join(enrich_customers, c)):
                        usecase_root = os.path.join(enrich_customers, c, usecase)
                        enrichjson = os.path.join(usecase_root, "enrich.json")
                        if not os.path.exists(enrichjson):
                            continue
                        data_root = os.path.join(enrich_data, c, usecase)
                        if not os.path.exists(data_root):
                            os.makedirs(data_root)
                            print(greenbg("data_root created: {}".format(data_root)))
                        else:
                            print(orangebg("data_root exists: {}".format(data_root)))


    enrich_root = os.environ["ENRICH_ROOT"]
    activate_cmd = None
    if "VIRTUAL_ENV" in os.environ:
        venv_root = os.environ["VIRTUAL_ENV"]
        venv_name = os.path.basename(venv_root)
        activate_cmd = f"source {venv_name}/bin/activate"
    elif "CONDA_PREFIX" in os.environ:
        venv_root = os.environ["CONDA_PREFIX"]
        venv_name = os.path.basename(venv_root)
        activate_cmd = f"conda activate {venv_name}"

    if activate_cmd is None:
        print(greenbg("env.sh not created"))
        return

    envsh = f"""\
{activate_cmd}
#workon {venv_name}
export ENRICH_ROOT={enrich_root}
"""

    with open(os.path.join(enrich_root, "env.sh"), "w") as fd:
        fd.write(envsh)
    print(greenbg("env.sh created"))


def checkenv(validate_only=False, context={}):
    """
    Check whether environment is correctly configured

    Parameters
    ----------
    None

    Yields
    ------
    Errors if any
    """

    variables = [
        "ENRICH_ROOT",
        "ENRICH_DATA",
        "ENRICH_TEST",
        "ENRICH_ETC",
        "ENRICH_SHARED",
        "ENRICH_VAR",
        "ENRICH_LIB",
        "ENRICH_OPT",
        "ENRICH_LOGS",
        "ENRICH_CUSTOMERS",
        "ENRICH_RELEASES",
        "ENRICH_CUSTOMERS",
        "ENRICH_TEST",
        # Tasks
        # "ENRICH_TASKDB_URL",
        # "ENRICH_TASKDB_HOSTNAME",
        # "ENRICH_TASKDB_PORT",
        # "ENRICH_TASKDB_LOGFILE",
        # Email
        # "EMAIL_HOST",
        # "EMAIL_HOST_USER",
        # "EMAIL_HOST_PASSWORD",
        # "EMAIL_PORT",
        # "EMAIL_USE_TLS"
    ]

    if not validate_only:
        print("Checking Environment")
        print("===============\n")

    for var in variables:
        if var in os.environ:
            if not validate_only:
                print(greenbg("{} defined".format(var)))
        else:
            if validate_only:
                return False
            print(redbg("{} NOT defined".format(var)))

    if validate_only:
        return True

    enrich_customers = os.environ["ENRICH_CUSTOMERS"]
    enrich_data = os.environ["ENRICH_DATA"]

    if not validate_only:
        print("\n")
        print("Checking Data Configuration")
        print("===============\n")

    valid = os.path.exists(enrich_customers)
    if not valid:
        print(redbg("ENRICH_CUSTOMERS is missing"))

    if valid:
        customers = os.listdir(enrich_customers)
        if len(customers) == 0:
            print(
                redbg(
                    "No applications linked in ENRICH_CUSTOMERS {}".format(
                        enrich_customers
                    )
                )
            )
        else:
            for c in customers:
                for usecase in os.listdir(os.path.join(enrich_customers, c)):
                    usecase_root = os.path.join(enrich_customers, c, usecase)
                    data_root = os.path.join(enrich_data, c, usecase)
                    if not (
                        os.path.isdir(usecase_root)
                        and os.path.exists(os.path.join(usecase_root, "enrich.json"))
                    ):
                        continue
                    if not os.path.exists(data_root):
                        print(redbg("data_root not created: {}".format(data_root)))
                    else:
                        print(greenbg("[{}] {} data_root exists".format(c, usecase)))

    siteconf = os.path.join(os.environ["ENRICH_ETC"], "siteconf.json")
    if isinstance(context, dict) and ("siteconf" in context):
        siteconf = context["siteconf"]
    if not os.path.exists(siteconf):
        print(redbg("siteconf missing: {}".format(siteconf)))
    else:
        try:
            json.load(open(siteconf))
            print(greenbg("Valid siteconf exists".format(siteconf)))
        except:
            print(redbg("siteconf exists but invalid"))

    versionmap = os.path.join(os.environ["ENRICH_ETC"], "versionmap.json")
    if isinstance(context, dict) and ("versionmap" in context):
        versionmap = context["versionmap"]
    if not os.path.exists(versionmap):
        print(redbg("versionmap missing: {}".format(versionmap)))
    else:
        try:
            json.load(open(versionmap))
            print(greenbg("Valid versionmap exists".format(siteconf)))
        except:
            print(redbg("versionmap exists but invalid"))

    return True


def print_log(logfile):
    """
    Show logfile
    """

    if not logfile.endswith(".json"):
        print("Requires a json file")
        return

    lines = open(logfile).readlines()
    lines = [l.strip() for l in lines]

    for l in lines:
        try:
            d = json.loads(l)
            print(
                " - ".join(
                    [
                        d[col]
                        for col in ["asctime", "application", "transform", "message"]
                        if col in d
                    ]
                )
            )
            if ("data" in d) and (len(d["data"]) > 0):
                data = d["data"]
                data = data.split("\n")
                data = ["     " + x for x in data]
                data = "\n".join(data)
                print("data:", data)
        except:
            print("Cannot parse ---")
            print(l)


######################################################
# Package testing...
######################################################


def print_exc(params):

    pkgdir = params["pkgdir"]
    formatted_lines = traceback.format_exc().splitlines()
    exists = any([pkgdir in l for l in formatted_lines])
    skip = True
    for l in formatted_lines:
        if pkgdir in l:
            skip = False
        if not skip or not exists:
            print(l)


####################################
# Pytest
####################################
def test_structure(params):

    assert "modname" in params
    assert "pkgdir" in params

    modname = params["modname"]
    pkgdir = params["pkgdir"]
    testdir = os.path.join(pkgdir, "tests")
    if not os.path.exists(testdir):
        print(redbg("Test directory missing"))

    return True


####################################
# Pytest
####################################
def test_pytest(params):

    assert "modname" in params
    assert "pkgdir" in params

    nextstep = False
    pkgdir = params["pkgdir"]

    nextstep = True
    import pytest

    exitcode = pytest.main([pkgdir])
    meaning = {
        0: "All tests were collected and passed successfully",
        1: "Tests were collected and run but some of the tests failed",
        2: "Test execution was interrupted by the user",
        3: "Internal error happened while executing tests",
        4: "pytest command line usage error",
        5: "No tests were collected",
    }

    if exitcode != 0:
        if exitcode in meaning:
            print(redbg(meaning[exitcode]))
        else:
            print(redbg("Pytest failed with unknown exit code: {}".format(exitcode)))
        nextstep = False
    else:
        print(greenbg("Completed successfully"))

    return nextstep


####################################
# Loading
####################################
def test_loading(params):

    assert "modname" in params
    assert "pkgdir" in params

    nextstep = False
    try:
        modname = params["modname"]
        pkgdir = params["pkgdir"]
        if params.get("isfile", False):
            file_, path_, desc_ = imp.find_module(modname, [pkgdir])
            params["mod"] = imp.load_module(modname, file_, path_, desc_)
        else:
            cmd = """import {}""".format(modname)
            exec(cmd)

        if modname not in sys.modules:
            print(redbg("Imported {} but cannot find in sys.modules".format(modname)))
        else:
            params["mod"] = sys.modules[modname]
            print(greenbg("Loaded imported the {} module".format(modname)))
            nextstep = True
    except:
        print(redbg("Unable to import {}".format(modname)))
        print_exc(params)

    return nextstep


####################################
# Instantiation
####################################
def test_instantiation(params):

    nextstep = False
    if "mod" not in params or params["mod"] is None:
        print(redbg("Cannot execute instantiation test. Missing module"))
        return nextstep

    mod = params["mod"]
    if not hasattr(mod, "provider"):
        print(redbg("Does not have a provider attribute"))
    else:
        print(greenbg("Module has a provider attribute"))
        nextstep = True

    if not nextstep:
        return nextstep

    provider = mod.provider
    try:
        config = params["config"]
        t = provider(config=config)
        params["obj"] = t
        nextstep = True
        print(greenbg("Able to instantiate the module"))
    except:
        print(redbg("Cannot instantiate the module"))
        print_exc(params)
        nextstep = False

    return nextstep


####################################
# Create mock state
####################################
def test_create_state(params):

    nextstep = False
    obj = params["obj"]
    config = params["config"]

    nextstep = False
    if not hasattr(obj, "testdata"):
        print(redbg("Module does not have or has invalid testdata to test execution"))
    else:
        print(greenbg("Module has testdata"))
        nextstep = True

    try:
        # If it is a lazy function, then call it now...
        if nextstep and callable(obj.testdata):
            obj.testdata = obj.testdata()
    except:
        print(redbg("Module could not load test data"))
        nextstep = False

    if not nextstep:
        return nextstep

    if hasattr(obj, "testdata"):
        if ("data" not in obj.testdata) or (not isinstance(obj.testdata["data"], dict)):
            print(redbg("Module's testdata should have dict 'data' element"))
            nextstep = False

        if nextstep and len(obj.testdata["data"]) == 0:
            print(orangebg("Module's testdata usually has non-trivial 'data' element"))

        if nextstep and obj.is_skin():
            if ("runs" not in obj.testdata) or (len(obj.testdata["runs"]) == 0):
                print(redbg("Renderer module's testdata should have 'runs' element"))
                nextstep = False

    if not nextstep:
        return nextstep

    try:
        obj.validate("testdata", None)
        print(greenbg("Testdata appears valid"))
    except:
        print(redbg("Testdata is invalid"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    if not hasattr(obj, "testdata"):
        raise Exception("Testdata attribute is missing")

    try:
        config.load_test_state(obj.testdata)
        print(greenbg("Able to load test data"))
    except:
        print(redbg("Module test data could not be loaded"))
        print_exc(params)
        nextstep = False

    return nextstep


####################################
# Execution
####################################
def test_execution_compute(params):

    obj = params["obj"]
    config = params["config"]
    state = config.get_state()

    nextstep = True

    try:
        conf = obj.get_test_conf()
        conf["test"] = True
        obj.configure(conf)
        print(greenbg("Configured the module"))
    except:
        print(redbg("Could not configure the module"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    try:
        obj.validate("conf", None)
        obj.validate("args", None)
        print(greenbg("Validated the configuration"))
    except:
        print(redbg("Could not validate the configuration"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    try:
        obj.validate("input", None)
    except:
        print(redbg("Could not validate input"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    # Run the computation
    try:
        print(greenbg("Starting process"))
        obj.process(state)
        print(greenbg("Executed the process function"))
    except:
        print(redbg("Could not execute process"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    # => Validate the results
    try:
        obj.validate("results", state)
        print(greenbg("Validated the results"))
    except:
        print(redbg("Invalid results"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    # => Store the results
    try:
        tmpdir = config.store_test_state(obj)
        print(greenbg("Stored the results"))
        print("Results in {}".format(tmpdir))
    except:
        print(redbg("Unable to store state"))
        print_exc(params)
        nextstep = False

    return nextstep


def test_execution(params):

    obj = params["obj"]
    config = params["config"]
    state = config.get_state()

    if obj.is_transform() or obj.is_model():
        return test_execution_compute(params)

    raise Exception("Unsupported module")


###############################################
# test_conf
###############################################
def load_single_transform(path, config):
    # => Now process
    modname = os.path.basename(path)
    dirname = os.path.dirname(path)

    if os.path.isfile(path):
        modname = modname.replace(".py", "")

    try:
        file_, path_, desc_ = imp.find_module(modname, [dirname])
        package = imp.load_module(modname, file_, path_, desc_)
    except:
        traceback.print_exc()
        raise Exception("Couldnt load transform: {}".format(modname))

    # => Load transform class..
    if not hasattr(package, "provider"):
        raise Exception("Transform has no provider")

    provider = package.provider

    try:
        p = provider(config=config)
    except:
        raise Exception("Could not instantiate transform")

    return p


def test_conf_pipeline(conf, context):
    """
    Test whether modules are present...
    """

    # => Collect all paths...
    params = {
        "enrich_run_root": os.environ["ENRICH_RUN_ROOT"],
        "enrich_root": os.environ["ENRICH_ROOT"],
        "enrich_customers_dir": os.environ["ENRICH_CUSTOMERS"],
        "enrich_data_dir": os.environ["ENRICH_DATA"],
    }

    usecase_root = conf.get("usecase_root", conf.get("customer_root", "Unknown"))
    params.update(
        {
            "usecase_root": usecase_root % params,
            # Backward compatability
            "customer_root": usecase_root % params,
            "data_root": conf["data_root"] % params,
        }
    )

    for col in ["data_root", "customer_root", "usecase_root"]:
        if not os.path.exists(params[col]):
            print(redbg("{} is missing".format(col)))

    config = MockConfig(context)
    config.load_usecase(conf["conf"])  # Pass path
    config.load_test_state({})

    # Prepare the sys path
    available = []

    packages = conf["paths"]["packages"]
    for pkg in packages:
        pkg = pkg % params
        transformdir = os.path.join(pkg, "transforms")
        if not os.path.exists(transformdir):
            continue
        for tname in os.listdir(transformdir):
            if tname.endswith("~") or tname == "__pycache__":
                continue
            fullpath = os.path.join(transformdir, tname, tname)
            try:
                t = load_single_transform(fullpath, config)
            except Exception as e:
                print(redbg("Invalid transform: {} ({})".format(str(e), fullpath)))
                continue
            print(greenbg("Loaded transform: {} => {}".format(tname, t.name)))
            available.append(t)

    libraries = conf["paths"]["libraries"]
    contribpath = os.path.join(os.path.dirname(__file__), "..", "contrib", "transforms")
    libraries.append(os.path.abspath(contribpath))
    for libdir in libraries:
        libdir = libdir % params
        if not os.path.exists(libdir):
            print(redbg("Library path {} is missing".format(libdir)))
            continue
        for tname in os.listdir(libdir):
            if tname.endswith("~") or tname in ["__pycache__", "__init__.py"]:
                continue
            for fullpath in [
                os.path.join(libdir, tname, "src", tname),
                os.path.join(libdir, tname, tname),
                os.path.join(libdir, tname),
            ]:
                if os.path.exists(fullpath):
                    break

            try:
                t = load_single_transform(fullpath, config)
            except Exception as e:
                print(redbg("Invalid transform: {} ({})".format(str(e), fullpath)))
                continue
            print(greenbg("Loaded transform: {} => {}".format(tname, t.name)))
            available.append(t)

    print("\n\nLooking for required Transforms:")
    for reqt in conf["transforms"]["enabled"]:
        name = reqt["transform"]
        args = reqt["args"]

        status = "missing"
        for avt in available:
            if avt.name == name:
                print(greenbg("Found {}".format(name)))
                status = "notconfigured"

            if status == "missing":
                continue

            try:
                avt.preload_clean_args(args)
                status = "configured"
            except Exception as e:
                print(redbg("Could not configure {}".format(name)))
                traceback.print_exc()
                break

            print(greenbg("Configured {}".format(name)))
            break

        if status == "missing":
            print(redbg("Could not find {}".format(name)))


def test_task_pipeline(conf, context):
    """
    Test whether modules are present...
    """

    # => Collect all paths...
    params = {
        "enrich_customers_dir": os.environ["ENRICH_CUSTOMERS"],
        "enrich_data_dir": os.environ["ENRICH_DATA"],
    }

    params.update(
        {
            "customer_root": conf["customer_root"] % params,
            "data_root": conf["data_root"] % params,
        }
    )

    config = MockConfig(context)
    config.load_usecase(conf["conf"])
    config.load_test_state({})

    libraries = conf["paths"]["libraries"]
    for l in libraries:
        l = l % params
        if not os.path.exists(l):
            continue
        sys.path.append(l)
        for d in os.listdir(l):
            try:
                impcmd = "from {} import *".format(d)
                exec(impcmd)
                print(greenbg("Loaded: {} from {}".format(d, l)))
            except:
                print(redbg("Could not load: {}".format(d)))

    def all_subclasses(cls):
        return cls.__subclasses__() + [
            g for s in cls.__subclasses__() for g in all_subclasses(s)
        ]

    tasks = [c.NAME for c in all_subclasses(Task)]

    print("\n\nKnown Tasks:")
    for t in tasks:
        print(greenbg("Loaded: " + t))

    print("\n\nRequired Tasks:")
    # Known tasks
    for t in conf["tasks"]:
        name = t["name"]
        if name not in tasks:
            print(redbg("Could not find {}".format(name)))
        else:
            print(greenbg("Found {}".format(name)))


def test_conf(conf, capture=False, context=None):
    """
    Unit test the pipeline configuration file

    Parameters
    ----------
    conf: configuration file

    Yields
    ------
    Success/failure for each of multiple sanity checks

    """

    context = Context(context).asdict()

    # Setup logging
    if capture:
        setup_logging()

    # => Add libraries from existing deployments
    load_customer_assets()

    if not conf.lower().endswith(".json") and not conf.lower().endswith(".py"):
        print(redbg("configuration file should end with .json or .py"))
        return
    else:
        print(greenbg("Valid suffix"))

    if not os.path.exists(conf):
        print(redbg("Configuration path doesnt exist: {}".format(conf)))
        return
    else:
        print(greenbg("Valid path"))

    try:
        if conf.lower().endswith(".json"):
            confobj = json.load(open(conf))
            confobj["conf"] = conf
        else:
            # Load python
            modname = "".join([x if x.isalnum() else "_" for x in conf])
            modspec = importlib.util.spec_from_file_location(modname, conf)
            mod = importlib.util.module_from_spec(modspec)
            modspec.loader.exec_module(mod)
            if not hasattr(mod, "config"):
                print(redbg("Module missing config element: {}".format(conf)))
                return
            confobj = mod.config
            confobj["conf"] = conf
    except:
        traceback.print_exc()
        print(redbg("Invalid configuration file"))
        return

    print(greenbg("Valid configuration file"))

    if "transforms" in confobj:
        test_conf_pipeline(confobj, context)
    else:
        test_task_pipeline(confobj, context)


###############################################
# test_transform
###############################################
def test_transform(pkgdir, capture=False, context=None):
    """
    Unit test the module (transforms and models for now)

    Recursively test all the packages within the specified target
    directory. This will test loading, instantiation, whether state
    being updated and execution.


    Parameters
    ----------
    pkgdir: Directory where the modules are.

    Yields
    ------
    Success/failure for each of multiple sanity checks

    """

    # Fix memory limits...
    set_limits()

    pkgdir = os.path.abspath(pkgdir)

    # Setup logging
    if capture:
        setup_logging()

    # => Add libraries from existing deployments
    load_customer_assets(context)

    # Cleanup pkgdir
    pkgdir = pkgdir.strip()
    if pkgdir.endswith("/"):
        pkgdir = pkgdir[:-1]

    if not os.path.exists(pkgdir):
        print("Invalid directory: {}".format(pkgdir))
        return

    config = MockConfig(context)

    # pkgdir could be
    #   x.py
    #   x/__init__.py
    #   x/x/__init__.py
    #   x/src/x/__init__.py
    #

    modname = None
    if os.path.isfile(pkgdir):
        dirname = os.path.dirname(pkgdir)
        modname = os.path.basename(pkgdir)
        modname = modname.split(".")[0]
    else:
        if not os.path.exists(os.path.join(pkgdir, "setup.py")):
            dirname = os.path.dirname(pkgdir)
            modname = os.path.basename(pkgdir)
        else:
            modname = os.path.basename(pkgdir)
            if os.path.exists(os.path.join(pkgdir, modname)):
                dirname = pkgdir
            elif os.path.exists(os.path.join(pkgdir, "src", modname)):
                dirname = os.path.join(pkgdir, "src")
            else:
                raise Exception("Unable to find module")

    sys.path.append(dirname)
    if modname is None:
        raise Exception("Could not load the module")

    # Load the enrich json available...
    try:
        config.load_usecase(pkgdir)
    except:
        raise Exception("Unable to load usecase details")

    params = {
        "path": pkgdir,
        "isfile": os.path.isfile(pkgdir),
        "pkgdir": dirname,
        "modname": modname,
        "config": config,
    }

    tests = [
        # test_structure,
        # test_pytest,
        test_loading,
        test_instantiation,
        test_create_state,
        test_execution,
    ]
    for i, t in enumerate(tests):
        nextstep = t(params)
        if not nextstep:
            if i < len(tests) - 1:
                print("Skipping the rest of the testing")
            break


###############################################
# testdata list
###############################################
def load_transform(pkgdir, capture, context):

    if capture:
        setup_logging()

    # => Add libraries from existing deployments
    load_customer_assets()

    # Cleanup pkgdir
    pkgdir = pkgdir.strip()
    if pkgdir.endswith("/"):
        pkgdir = pkgdir[:-1]

    if not os.path.exists(pkgdir):
        print("Invalid directory: {}".format(pkgdir))
        return None

    # Add it to the path..
    sys.path.append(pkgdir)

    # Load the module...
    found = False
    for dirname, subdirs, files in os.walk(pkgdir):

        if "setup.py" not in files:
            continue

        found = True
        print("\nChecking: {}".format(dirname))
        break

    if not found:
        print(redbg("Not a valid transform package"))
        return None

    # Create a config and load customer
    config = MockConfig(context)
    config.load_usecase(dirname)

    params = {
        "pkgdir": dirname,
        "modname": os.path.basename(dirname),
        "config": config,
    }

    tests = [
        # test_structure,
        # test_pytest,
        test_loading,
        test_instantiation,
        test_create_state,
    ]

    failure = False
    for i, t in enumerate(tests):
        nextstep = t(params)
        failure = not nextstep
        if failure:
            if i < len(tests) - 1:
                print("Skipping the rest of the testing")
                break

    if failure:
        return

    obj = params["obj"]
    state = config.get_state()

    try:
        conf = obj.get_test_conf()
        conf["test"] = True
        obj.configure(conf)
        print(greenbg("Configured the module"))
    except:
        print(redbg("Could not configure the module"))
        print_exc(params)

    return params


def load_spec(specfile, capture):

    if capture:
        setup_logging()

    # => Add libraries from existing deployments
    load_customer_assets()

    if not os.path.exists(specfile):
        print(redbg("Invalid file: {}".format(specfile)))
        return None

    # Load python
    try:
        specfile = os.path.abspath(specfile)
        modname = "".join([x if x.isalnum() else "_" for x in specfile])
        modspec = importlib.util.spec_from_file_location(modname, specfile)
        mod = importlib.util.module_from_spec(modspec)
        modspec.loader.exec_module(mod)
        if not hasattr(mod, "registry"):
            print(redbg("Module missing datasets element: {}".format(specfile)))
            return
    except:
        traceback.print_exc()
        print(redbg("Unable to load module"))
        return

    return mod.registry


def testdata_transform_list(pkgdir, capture, context):
    """
    List the available datasets to process

    Parameters
    ----------
    pkgdir: Directory where the modules are.

    Yields
    ------
    A list of available datasets

    """

    # Load the transform...
    params = load_transform(pkgdir, capture, context)
    if params is None:
        print(redbg("Could not load the transform"))
        return

    # now check the testdata
    transform = params["obj"]
    if "datasets" not in transform.testdata:
        print(redbg("No datasets specified in testdata"))
        return

    datasets = transform.testdata["datasets"]
    available = datasets.get("available", [])
    for i, d in enumerate(available):
        print("[{:2}] {}".format(i, d))


def testdata_spec_list(specfile, capture, context):
    """
    List the available datasets to process

    Parameters
    ----------
    spec: specfile

    Yields
    ------
    A list of available datasets

    """

    # Load the transform...
    registry = load_spec(specfile, capture)
    if registry is None:
        print("Registry not found")
        return

    for i, d in enumerate(registry.list()):
        print("[{:2}] {}".format(i, d))


def testdata_transform_show(pkgdir, capture, context, name):
    """
    Show details of a dataset

    Parameters
    ----------
    pkgdir: Directory where the modules are.

    Yields
    ------
    A list of available datasets

    """

    # Load the transform...
    params = load_transform(pkgdir, capture, context)
    if params is None:
        print(redbg("Could not load the transform"))
        return

    transform = params["obj"]
    config = params["config"]

    if "datasets" not in transform.testdata:
        print(redbg("No datasets specified in testdata"))
        return

    datasets = transform.testdata["datasets"]
    datasets = transform.testdata["datasets"]
    available = datasets.get("available", [])
    extra = datasets.get("params", {})

    found = False
    for d in available:
        if d.name == name:
            found = True
            break

    if not found:
        print(redbg("Dataset {} not found".format(name)))
        return

    print(greenbg("Found dataset - {}".format(name)))

    print("Description:", d.description)

    print("------")
    print("[Targets] Available")
    print("------")

    for p in d.get_paths():
        name = p["name"]
        path = p["path"]
        print("  [{}] {}".format(name, path))

    print("[match] Pattern:", d.match["pattern"])

    dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    examples = d.generate(end=dt, start=dt + timedelta(days=-7))

    for example in examples:
        print("   :", example["timestamp"], "=>", example["name"])


def testdata_spec_show_file(config, registry, dataset):
    """
    Show commands involving a file
    """

    extra = registry.params

    print("[Targets] Available ", end="")
    print("(files)" if dataset.isfile else "(dirs)")
    print("------")
    for p in dataset.get_paths():
        name = p["name"]
        path = p["path"]
        nature = p["nature"]
        resolved = config.get_file(path, extra=extra, abspath=False)
        print("  [{}] (type: {}) {}".format(name, nature, resolved))

    print("------")
    print("[match] Pattern:", dataset.match["pattern"])
    print("------")
    dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    examples = dataset.generate(end=dt, start=dt + timedelta(days=-7))

    for example in examples:
        print("   :", example["timestamp"], "=>", example["name"])

    print("------")
    print("Supported Commands")
    print("------")
    targets = defaultdict(list)
    for p in dataset.get_paths():
        name = p["name"]
        nature = p["nature"]
        targets[nature].append(name)

    for c in registry.get_commands(source_type="File"):
        name = c["name"]
        desc = c["description"]
        args = c["args"]

        found = True
        for arg in args:
            values = arg.find(dataset)
            if (
                (values is None)
                or (values in [""])
                or ((isinstance(values, list)) and (len(values) == 0))
            ):
                found = False
        if not found:
            continue

        print("\n[{}] {}".format(name, desc))
        example = ""
        for arg in args:
            values = arg.find(dataset)

            if not isinstance(values, list):
                values = [str(values)]
            else:
                values = [str(v) for v in values]
            print("   {:10s}:".format(arg.name), ",".join(values))

            example += "{}='{}' ".format(arg.name, values[0])
        print("\n   Example: ...", name, example)


def testdata_spec_show_database(config, registry, dataset):
    """
    Show commands involving a database
    """
    for c in registry.get_commands(source_type="DBTable"):
        pass


def testdata_spec_show(specfile, capture, context, name):
    """
    Show details of a dataset

    Parameters
    ----------
    pkgdir: Directory where the modules are.

    Yields
    ------
    A list of available datasets

    """

    context = Context(context).asdict()
    config = MockConfig(context)

    # Load the transform...
    registry = load_spec(specfile, capture)
    if registry is None:
        print(redbg("Registry is None"))
        return

    print(greenbg("Found registry"))

    extra = registry.params

    dataset = registry.find(name)
    if dataset is None:
        print(redbg("Dataset {} not found".format(name)))
        return

    print(greenbg("Found dataset - {}".format(name)))

    extra.pop("enrich_data_dir", None)
    extra.update(
        {
            "enrich_data_dir": os.path.expandvars("$ENRICH_DATA"),
        }
    )

    print("Description:", dataset.description)
    print("------")
    if dataset._type == "File":
        testdata_spec_show_file(config, registry, dataset)


def testdata_transform_action(pkgdir, capture, context, name, target, start, end):
    """
    Show details of a dataset

    Parameters
    ----------
    pkgdir: Directory where the modules are.

    Yields
    ------
    A list of available datasets

    """

    # Load the transform...
    params = load_transform(pkgdir, capture, context)
    if params is None:
        print(redbg("Could not load the transform"))
        return

    transform = params["obj"]
    config = params["config"]

    if "datasets" not in transform.testdata:
        print(redbg("No datasets specified in testdata"))
        return

    datasets = transform.testdata["datasets"]
    available = datasets.get("available", [])
    extra = datasets.get("params", {})
    command = datasets.get(
        "command", "[%(timestamp)s]: %(backuppath)s => %(targetpath)s"
    )

    found = False
    for d in available:
        if d.name == name:
            found = True
            break

    if not found:
        print(redbg("Dataset {} not found".format(name)))
        return

    print(greenbg("Found dataset - {}".format(name)))

    print("------")
    print("Description:", d.description)
    print("------")

    testpath = config.get_file(d.test, extra=extra, abspath=False)
    print("[test]", testpath)

    localpath = config.get_file(d.local, extra=extra)
    print("[local]", localpath)

    backuppath = config.get_file(d.backup, extra=extra, abspath=False)
    print("[backup]", backuppath)
    print("[match] Pattern:", d.match["pattern"])

    start = dateparser.parse(start)  # naive datetime
    end = dateparser.parse(end)

    combinations = d.generate(end=end, start=start)
    for c in combinations:
        params = copy.copy(extra)
        testpath = os.path.join(testpath, c["name"])
        localpath = os.path.join(localpath, c["name"])
        targetpath = testpath if target == "test" else localpath
        params.update(
            {
                "targetpath": targetpath,
                "backuppath": os.path.join(backuppath, c["name"]),
            }
        )
        print(command % params)


def testdata_spec_action(specfile, capture, context, name, command, **kwargs):
    """
    Show details of a dataset

    Parameters
    ----------
    pkgdir: Directory where the modules are.

    Yields
    ------
    A list of available datasets

    """

    context = Context(context).asdict()
    config = MockConfig(context)

    # Load the transform...
    registry = load_spec(specfile, capture)
    if registry is None:
        print(redbg("Registry is None"))
        return

    print(greenbg("Found registry"))

    extra = registry.params

    dataset = registry.find(name)
    if dataset is None:
        print(redbg("Dataset {} not found".format(name)))
        return

    print(greenbg("Found dataset - {}".format(name)))

    extra.pop("enrich_data_dir", None)
    extra.update(
        {
            "enrich_data_dir": os.path.expandvars("$ENRICH_DATA"),
        }
    )

    print("------")
    print("Description:", dataset.description)
    print("------")

    try:
        command = registry.get_command(command)
    except:
        print(redbg("Command {} could not be found".format(command)))
        return

    print("Command")
    print("   ", command["command"])
    print("------")

    resolve = {}
    args = command["args"]
    for arg in args:
        name = arg.name
        if arg.name not in kwargs:
            raise Exception(
                "Missing argument '{}' ({})".format(arg.name, arg.description)
            )

        value = kwargs[arg.name]
        if not arg.validate(dataset, value):
            raise Exception(
                "Invalid argument '{}' ({}) has value '{}'".format(
                    arg.name, arg.description, value
                )
            )

        try:
            resolve[arg.name] = arg.resolve(dataset, value, resolve=registry.params)
        except:
            raise Exception(
                "Invalid argument '{}' ({}) has value '{}'".format(
                    arg.name, arg.description, value
                )
            )

    if ("start" not in resolve) or ("end" not in resolve):
        raise Exception("'start' and 'end' datetime values are required")

    print("Args")
    print("------")
    for a in args:
        print("   ", a.name, ":", resolve[a.name])
    print("")

    print("[commands] Please run these after checking")
    combinations = dataset.generate(end=resolve["end"], start=resolve["start"])
    for c in combinations:
        params = copy.copy(registry.params)
        params["source"] = resolve["src"]
        params["destination"] = resolve["dst"]
        params["subdir"] = c["name"]
        params["slash"] = "" if dataset.isfile else "/"

        try:
            print(command["command"] % params)
        except Exception as e:
            print(redbg("Could not generate command"))
            print(redbg("Please check registry params"))
            print("Error:", str(e))
            return


def testdata_action(action, *args, **kwargs):

    spec = args[0]

    if os.path.isdir(spec):
        print(redbg("Deprecated. Use the dataset file"))
        return

        if action == "list":
            testdata_transform_list(*args, **kwargs)
        elif action == "show":
            testdata_transform_show(*args, **kwargs)
        elif action == "action":
            testdata_transform_action(*args, **kwargs)
    else:
        if action == "list":
            testdata_spec_list(*args, **kwargs)
        elif action == "show":
            testdata_spec_show(*args, **kwargs)
        elif action == "action":
            testdata_spec_action(*args, **kwargs)


###############################################
# Main test
###############################################
def test_task_instantiation(params):

    nextstep = False
    if "mod" not in params or params["mod"] is None:
        print(redbg("Cannot execute instantiation test. Missing module"))
        return nextstep

    mod = params["mod"]
    clsmembers = inspect.getmembers(mod, inspect.isclass)
    # [('OrderedDict', <class 'collections.OrderedDict'>), ('StoreMetadataTask', <class 'store_metadata.StoreMetadataTask'>), ('Task', <class 'enrichsdk.tasks.Task'>)]
    # [('AnalyzeS3SourceBaseTask', <class 'enrichapp.core.tasks.analyzesource.AnalyzeS3SourceBaseTask'>), ('AnalyzeS3SourceDefaultTask', <class 'analyzesource.AnalyzeS3SourceDefaultTask'>)]

    clsmembers = [c for c in clsmembers if issubclass(c[1], Task) and c[1] is not Task]

    if len(clsmembers) == 0:
        print(redbg("Does not have any task classes"))
    else:
        print(greenbg("Module has task classes"))
        nextstep = True

    if not nextstep:
        return nextstep

    if len(clsmembers) > 1:
        print(orangebg("Module has more than task. Testing only one"))
        provider = None
        modpath = mod.__file__
        for c in clsmembers:
            path = inspect.getfile(c[1])
            if path == modpath:
                provider = c[1]

        if provider is None:
            # Could not locate the right task to test
            print(orangebg(str(clsmembers)))
            print(orangebg(str("Mod path", modpath)))
            raise Exception("Could not find right task provider class to test")
    else:
        provider = clsmembers[0][1]

    try:
        config = params["config"]
        t = provider(config=config)
        params["obj"] = t
        nextstep = True
        print(greenbg("Able to instantiate the module"))
    except:
        print(redbg("Cannot instantiate the module"))
        print_exc(params)
        nextstep = False

    return nextstep


def test_task_create_state(params):

    nextstep = False
    obj = params["obj"]
    config = params["config"]

    nextstep = False
    if not hasattr(obj, "testdata"):
        print(redbg("Module does not have or has invalid testdata to test execution"))
    else:
        print(greenbg("Module has testdata"))
        nextstep = True

    if hasattr(obj, "testdata"):
        # If callable, then call it...
        try:
            if callable(obj.testdata):
                obj.testdata = obj.testdata()
        except:
            print(redbg("Module could not load test data"))
            nextstep = False

        if not nextstep:
            return nextstep

        if ("data" not in obj.testdata) or (not isinstance(obj.testdata["data"], dict)):
            print(redbg("Module's testdata should have dict 'data' element"))
            nextstep = False

        if nextstep and len(obj.testdata["data"]) == 0:
            print(orangebg("Module's testdata usually has non-trivial 'data' element"))

    if not nextstep:
        return nextstep

    try:
        obj.validate("testdata", None)
        print(greenbg("Testdata appears valid"))
    except:
        print(redbg("Testdata is invalid"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    try:
        config.load_test_state(obj.testdata)
        print(greenbg("Able to load test data"))
    except:
        print(redbg("Module test data could not be loaded"))
        print_exc(params)
        nextstep = False

    return nextstep


def test_task_load_testdata(params):

    nextstep = False
    obj = params["obj"]
    config = params["config"]

    nextstep = False
    if not hasattr(obj, "testdata"):
        print(redbg("Module does not have or has invalid testdata to test execution"))
    else:
        print(greenbg("Module has testdata"))
        nextstep = True

    if hasattr(obj, "testdata"):
        if ("data" not in obj.testdata) or (not isinstance(obj.testdata["data"], dict)):
            print(redbg("Module's testdata should have dict 'data' element"))
            nextstep = False

        if nextstep and len(obj.testdata["data"]) == 0:
            print(orangebg("Module's testdata usually has non-trivial 'data' element"))

    if not nextstep:
        return nextstep

    try:
        obj.validate("testdata", None)
        print(greenbg("Testdata appears valid"))
    except:
        print(redbg("Testdata is invalid"))
        print_exc(params)
        nextstep = False

    return nextstep


def test_task_execution_compute(params):

    obj = params["obj"]
    config = params["config"]
    state = config.get_state()

    nextstep = True

    try:
        config_params = obj.testdata.get("config", {})
        config.configure(config_params)
    except:
        print(redbg("Could not configure the mock pipeline executor"))
        print_exc(params)
        nextstep = False

    try:
        conf = obj.testdata.get("conf", {})
        obj.configure(conf)
        print(greenbg("Configured the module"))
    except:
        print(redbg("Could not configure the module"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    try:
        obj.validate("conf", state)
        obj.validate("args", state)
        print(greenbg("Validated the configuration"))
    except:
        print(redbg("Could not validate the configuration"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    # Run the computation
    try:
        print(greenbg("Starting task execution"))
        obj.run(state)
        print(greenbg("Executed the process function"))
    except:
        print(redbg("Could not execute process"))
        print_exc(params)
        nextstep = False

    if not nextstep:
        return nextstep

    # => Validate the results
    try:
        obj.validate("results", state)
        print(greenbg("Validated the results"))
    except:
        print(redbg("Invalid results"))
        print_exc(params)
        nextstep = False

    print("State")
    print(state.state)

    return nextstep


def test_task(taskdir, capture=False, context=None):
    """
    Unit test the task module

    Parameters
    ----------
    tasklib: Directory where the task lib is

    Yields
    ------
    Success/failure for each of multiple sanity checks
    """

    context = Context(context).asdict()

    if capture:
        setup_logging()

    # => Add libraries from existing deployments
    load_customer_assets()

    # Cleanup pkgdir
    taskdir = taskdir.strip()
    if taskdir.endswith("/"):
        taskdir = taskdir[:-1]

    if not os.path.exists(taskdir) or os.path.isfile(taskdir):
        print("Invalid directory: {}".format(taskdir))
        return

    # Add it to the path..
    dirname = os.path.dirname(taskdir)
    sys.path.append(dirname)

    params = {
        "pkgdir": dirname,
        "modname": os.path.basename(taskdir),
        "config": MockConfig(context),
    }

    tests = [
        test_loading,
        test_task_instantiation,
        test_task_create_state,
        test_task_load_testdata,
        test_task_execution_compute,
    ]

    for i, t in enumerate(tests):
        nextstep = t(params)
        if not nextstep:
            if i < len(tests) - 1:
                print("Skipping the rest of the testing")
                break
