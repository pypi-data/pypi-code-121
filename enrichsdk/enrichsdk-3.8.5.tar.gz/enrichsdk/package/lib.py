import os
from jinja2 import Environment, FileSystemLoader, PackageLoader, meta

thisdir = os.path.dirname(__file__)
default_templatedir = os.path.abspath(os.path.join(thisdir, "..", "templates"))

# from prompt_toolkit.token import Token
# from prompt_toolkit.styles import style_from_dict
# style = style_from_dict({
#    Token.Toolbar: '#ffffff bg:#333333',
# })


##########################
# Jinja2 helper functions...
##########################
def get_template_path(filename, templatedir=None):

    if os.path.isabs(filename):
        return filename

    if templatedir is None:
        templatedir = default_templatedir

    # Check if relative path is specified, then use it.
    # if os.path.exists(filename):
    #   return filename

    return os.path.join(templatedir, filename)


def list_templates(suffix=".node.template"):

    mapping = {}
    for t in os.listdir(default_templatedir):
        if t.endswith(suffix):
            path = os.path.join(default_templatedir, t)
            mapping[t.replace(suffix, "")] = path
    return mapping


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


def write_rendered_file(templatefile, target, filename, params):

    if not templatefile.startswith("/"):
        templatefile = get_template_path(templatefile)

    if not os.path.exists(templatefile):
        raise Exception("Template file doesnt exist")

    content = render(templatefile, params)
    try:
        os.makedirs(target)
    except:
        pass

    with open(os.path.join(target, filename), "w") as fd:
        fd.write(content)
    return content
