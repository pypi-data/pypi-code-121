import os, json, shutil, traceback
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader, PackageLoader, meta

from prompt_toolkit import prompt
from prompt_toolkit.token import Token
from prompt_toolkit.contrib.completers import PathCompleter
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.contrib.completers import WordCompleter

##########################
# Jinja2 helper functions...
##########################
def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return (
        Environment(loader=FileSystemLoader(path or "./"))
        .get_template(filename)
        .render(context)
    )


def get_variables(tpl_path):
    path, filename = os.path.split(tpl_path)
    env = Environment(loader=FileSystemLoader(path or "./"))
    template_source = env.loader.get_source(env, filename)[0]
    parsed_content = env.parse(template_source)
    return meta.find_undeclared_variables(parsed_content)


style = style_from_dict(
    {
        Token.Toolbar: "#ffffff bg:#333333",
    }
)

#################################################
# Helper
#################################################
def welcome():
    print("==============================")
    print("  Welcome to Scribble Enrich ")
    print("=============================")
    print("\n\n")


def read_globalconf():
    confpath = os.path.expanduser("~/.enrich.json")
    if os.path.exists(confpath):
        conf = json.loads(open(confpath).read())
    else:
        conf = {"workspaces": ["enrich-data"]}
    return conf


def write_globalconf(conf):
    confpath = os.path.expanduser("~/.enrich.json")
    with open(confpath, "w") as fd:
        fd.write(json.dumps(conf, indent=4))


#################################################
# Validators
#################################################
class NameValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Customer name should not be empty",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class DescValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Customer description should not be empty",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class LogoValidator(Validator):
    def validate(self, document):
        url = document.text
        if len(url) == 0:
            raise ValidationError(
                message="Customer logo URL should not be empty",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.
        if not url.startswith("http"):
            raise ValidationError(
                message="Customer logo URL should be a valid URL (http://...",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.
        if not (
            url.lower().endswith("png")
            or url.lower().endswith("gif")
            or url.lower().endswith("jpg")
            or url.lower().endswith("ico")
        ):
            raise ValidationError(
                message="Customer logo URL should be a valid URL (http://....png",
                cursor_position=len(document.text),
            )  # Move cursor to end of input.


class ValidDir(Validator):
    def validate(self, document):
        if (
            (len(document.text) == 0)
            or (not os.path.exists(document.text))
            or (not os.path.isdir(document.text))
        ):
            raise ValidationError(
                message="Directory specified doesnt exist or is invalid",
                cursor_position=len(document.text),
            )


class ValidFile(Validator):
    def validate(self, document):
        if (
            (len(document.text) == 0)
            or (not os.path.exists(document.text))
            or (not os.path.isfile(document.text))
        ):
            raise ValidationError(
                message="File specified doesnt exist or is invalid",
                cursor_position=len(document.text),
            )


##########################
# Management
##########################
def create_workspace(workspace, context):

    # Create the directories
    try:
        os.makedirs(workspace)
    except:
        pass

    for subdir in [".", "conf", "output", "data", "transforms"]:
        try:
            os.makedirs(os.path.join(workspace, context["name"], subdir))
        except:
            pass

    # Now write the enrich.json
    thisdir = os.path.dirname(__file__)
    template = os.path.join(thisdir, "templates", "enrich.json.template")

    updated = render(template, context)
    enrichfile = os.path.join(workspace, context["name"], "enrich.json")
    with open(enrichfile, "w") as fd:
        fd.write(updated)


def prepare_workspace():

    welcome()

    print("We will ask you a few question\n")

    # => Directory
    path_completer = PathCompleter()
    workspace = prompt(
        "> Workspace directory: ",
        default="enrich-data",
        style=style,
        completer=path_completer,
    )

    print("\nWe need some additional input about the customer:\n")

    validators = {
        "name": NameValidator(),
        "description": DescValidator(),
        "logourl": LogoValidator(),
    }

    context = {}
    variables = get_variables(template)
    for v in variables:
        context[v] = prompt("> " + v + ": ", validator=validators.get(v, None))

    # => Update the global conf file...
    conf = read_globalconf()
    if workspace not in conf["workspaces"]:
        conf["workspaces"].append(workspace)
    write_globalconf(conf)


def prepare_transform():

    welcome()

    print("Bootstrapping a transform\n")

    conf = read_globalconf()
    workspaces = conf["workspaces"]

    # => Get workspace
    word_completer = WordCompleter(workspaces, ignore_case=True)
    if os.path.exists("enrich-data"):
        defaultdir = "enrich-data"
    else:
        defaultdir = "."

    workspace = prompt(
        "> Workspace: ",
        default=defaultdir,
        completer=word_completer,
        validator=ValidDir(),
    )

    # => Select the customer
    customers = os.listdir(workspace)
    if len(customers) == 0:
        print(
            "Looks like you havent created the workspace properly. Please run bootstrap workspace"
        )
        return

    customer_completer = WordCompleter(customers, ignore_case=True)
    customer = prompt(
        "> Customer: ", default=customers[0], completer=customer_completer
    )

    # => Bootstrap a template
    templatedir = os.path.join(os.path.dirname(__file__), "templates")

    # => Load the manifest
    print("\nPlease provide transform details\n")
    defaults = {"version": "1.0", "minorversion": "1.0"}
    validators = {"name": NameValidator(), "description": DescValidator()}
    manifest_template = os.path.join(templatedir, "manifest.json.template")
    context = {}
    variables = get_variables(manifest_template)
    for v in variables:
        context[v] = prompt(
            "> " + v + ": ",
            default=defaults.get(v, ""),
            validator=validators.get(v, None),
        )
    node_manifest = render(manifest_template, context)

    readme_template = os.path.join(templatedir, "README.md.template")
    node_readme = render(readme_template, context)

    # Get the right template
    templates = [t for t in os.listdir(templatedir) if t.endswith(".node.template")]
    templates = [t.replace(".node.template", "") for t in templates]
    template_completer = WordCompleter(templates, ignore_case=True)
    node = prompt(
        "> Type of Transform: ", default=templates[0], completer=template_completer
    )

    template_file = os.path.join(templatedir, "{}.node.template".format(node))
    node_content = render(template_file, context)

    # => Now you are ready to write
    transform_dir = os.path.join(workspace, customer, "transforms", context["name"])
    try:
        os.makedirs(transform_dir)
    except:
        pass

    with open(os.path.join(transform_dir, "__init__.py"), "w") as fd:
        fd.write(node_content)

    with open(os.path.join(transform_dir, "manifest.json"), "w") as fd:
        fd.write(node_manifest)

    with open(os.path.join(transform_dir, "README.md"), "w") as fd:
        fd.write(node_readme)

    # Bye bye
    print("Bootstrapped transform {} in {}".format(context["name"], transform_dir))


def prepare_config():

    welcome()

    print("Bootstrapping a new configuration\n")

    conf = read_globalconf()
    workspaces = conf["workspaces"]

    # => Get workspace
    word_completer = WordCompleter(workspaces, ignore_case=True)
    if os.path.exists("enrich-data"):
        defaultdir = "enrich-data"
    else:
        defaultdir = "."
    workspace = prompt(
        "> Workspace: ",
        default=defaultdir,
        completer=word_completer,
        validator=ValidDir(),
    )

    # => Select the customer
    usecases = os.listdir(workspace)
    if len(usecases) == 0:
        print(
            "Looks like you havent created the workspace properly. Please run bootstrap workspace"
        )
        return

    usecase_completer = WordCompleter(usecases, ignore_case=True)
    usecase = prompt("> Usecase: ", default=usecases[0], completer=usecase_completer)

    templatedir = os.path.join(os.path.dirname(__file__), "templates")
    validators = {"name": NameValidator(), "description": DescValidator()}

    print("\nPlease provide configuration details\n")
    config_template = os.path.join(templatedir, "config.json.template")
    context = {}
    variables = get_variables(config_template)
    for v in variables:
        context[v] = prompt("> " + v + ": ", validator=validators.get(v, None))
    config = render(config_template, context)

    name = context["name"]
    cleaned_name = "".join([x if x.isalnum() else "_" for x in name.lower()])
    configfile = os.path.join(
        workspace, customer, "conf", "{}.json".format(cleaned_name)
    )
    with open(configfile, "w") as fd:
        fd.write(config)

    # Bye bye
    print("Bootstrapped configuration {} in {}".format(context["name"], configfile))


def bootstrap(what):

    if what == "workspace":
        prepare_workspace()
    elif what == "transform":
        prepare_transform()
    elif what == "config":
        prepare_config()


def bootstrap1(config, transform, transformtype):
    """
    Initialize a new pipeline...
    """
    thisdir = os.path.dirname(__file__)

    # => First ensure that the destination exists
    if not os.path.exists(config):
        os.makedirs(config)
    elif os.path.isfile(config):
        raise Exception("Config path cannot be a file")

    # => Not install the transform
    if transform not in ["none", None]:

        transform_path = os.path.join(config, "transforms", transform)

        try:
            os.makedirs(transform_path)
        except:
            pass

        contentpath = os.path.join(thisdir, "{}.template".format(transformtype))
        if not os.path.exists(contentpath):
            raise Exception("Unsupported transform type template. Use generic")

        content = open(contentpath).read()
        initfile = os.path.join(transform_path, "__init__.py")
        with open(initfile, "w") as fd:
            fd.write(content)

        # Insert a manifest as well...
        manifest = os.path.join(transform_path, "manifest.json")
        with open(manifest, "w") as fd:
            fd.write(
                json.dumps(
                    {
                        "name": "MyModule",
                        "version": 1.0,
                        "minorversion": 1.0,
                        "params": [
                            {
                                "name": "Path",
                                "required": True,
                                "description": """\
Path for the module such as 
c:\path\to\file 
/path/to/file
""",
                            }
                        ],
                    },
                    indent=4,
                )
            )


############################################################
# Convert
############################################################
def convert(what, src, dst):
    """
    Take the old style transform skin and convert into a package each.
    """
    if os.path.exists(dst):
        raise Exception("Destination exists. Please remove it.")

    if not os.path.exists(src):
        raise Exception("Source does not exist. Invalid directory")

    basename = os.path.basename(src)
    try:
        enrichjson = os.path.abspath(os.path.join(src, "..", "..", "enrich.json"))
        usecase = json.load(open(enrichjson))
    except:
        traceback.print_exc()
        usecase = {"org": {"name": "Unknown", "customer": "Unknown"}}

    try:
        manifestcontent = json.load(open(os.path.join(src, "manifest.json")))
    except:
        manifestcontent = {}

    # =>
    defaults = {
        "what": what,
        "basename": basename,
        "name": basename,
        "version": "0.1",
        "description": basename + " package",
        "author": "Scribble Data",
        "email": "support@scribbledata.io",
        "url": "https://github.com/scribbledata/scribble-enrichsdk",
        "customer": usecase["org"]["name"],
        "usecase": usecase["org"]["name"],
    }

    params = {}
    for k, v in defaults.items():
        params[k] = manifestcontent.get(k, v)

    # Prepare the destination
    os.makedirs(dst)

    # Copy the code
    shutil.copytree(src, os.path.join(dst, basename))

    # => Write the manifest file
    # Write the manifest file...
    manifest = """\
include LICENSE
recursive-include %(basename)s *py *.html *md *template *json
"""
    manifest = manifest % params
    with open(os.path.join(dst, "MANIFEST.in"), "w") as fd:
        fd.write(manifest)

    # => Write license content
    license = """\
All rights reserved (c) Scribble Data          
"""
    with open(os.path.join(dst, "LICENSE"), "w") as fd:
        fd.write(license)

    # => Write the setup file
    setupcontent = """\
import os
from setuptools import setup

setup(name='%(basename)s',
      version='%(version)s',
      description='%(description)s',
      url='%(url)s', 
      author='%(author)s',
      author_email='%(email)s', 
      license='None',
      packages=['%(basename)s'],
      zip_safe=True,
      include_package_data=True,
      entry_points={
          '%(customer)s.%(what)s': ['%(basename)s=%(basename)s'],
      },
)
"""
    setupcontent = setupcontent % params

    with open(os.path.join(dst, "setup.py"), "w") as fd:
        fd.write(setupcontent)

    print("Created a package in {}".format(dst))
