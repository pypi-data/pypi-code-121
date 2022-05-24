import os
import re
import six
import click
from sumoappclient.common.logger import get_logger
from sumoapputils.common.utils import touch, USER
from sumoappclient.common.utils import get_normalized_path

logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

if six.PY2:
    input = raw_input

@click.group()
def initializeapp():
    pass


def validate_folder(ctx, param, value):
    app_folder = os.path.basename(get_normalized_path(value))
    if re.match(r'^[a-zA-Z0-9_]+$', app_folder):
        return value
    else:
        raise click.BadOptionUsage(option_name=param.name, message="Folder name: %s should contain only upper and lowercase letters, numbers, and underscores." % value, ctx=ctx)


README_TEMPLATE='''
# %s

%s

# Documentation
  <Provide app docs link>
    
'''
@initializeapp.command(help="For generating initial structure of app folder")
@click.option('-a', '--appname', required=True, help='Sets app name')
@click.option('-t', '--target_directory', type=click.Path(dir_okay=True, file_okay=False), default=os.getcwd(), prompt=True, required=True, help='Sets dir name', callback=validate_folder)
def init(appname, target_directory):
    app_folder = get_normalized_path(target_directory)
    if not os.path.isdir(app_folder):
        print("Creating directory: %s" % app_folder)
        os.mkdir(app_folder)

    file_name = appname.replace(" ", '').replace("_", "") + ".json"
    touch(os.path.join(app_folder, file_name))
    if USER.is_partner:
        res_folder = os.path.join(app_folder, "resources")
        os.mkdir(res_folder)
        os.mkdir(os.path.join(res_folder, "screenshots"))
        os.mkdir(os.path.join(res_folder, "icon"))
        os.mkdir(os.path.join(res_folder, "logs"))
        app_description = input("Enter app description > ")
        readme_filepath = os.path.join(app_folder, "README.md")
        if not os.path.isfile(readme_filepath):
            with open(readme_filepath, "w") as f:
                f.write(README_TEMPLATE % (appname, app_description))

        with open(os.path.join(app_folder, ".gitignore"), "a+") as f:
            content = f.read()
            if "testlogs" not in content:
                f.write("testlogs/\n")
