#
# Module containing helpers to scan through files
#
import os
import re
import fnmatch

from databutton.utils import DEFAULT_GLOB_EXCLUDE, get_databutton_config

# Find all modules we need to import
# 1. Traverse all sub-directories under rootdir
# 2. Find all python files containing a decorator
# 3. If __init__.py doesn't exist in a subdir with a decorator, create it
# 4. Rename python filename to an importable module name
# 5. Return list of modules to import


def find_databutton_directive_modules(rootdir=os.curdir):
    try:
        config = get_databutton_config()
    except FileNotFoundError:
        config = None
    excludes = config.exclude if config else DEFAULT_GLOB_EXCLUDE
    modules_to_import = []
    for root, dirs, files in os.walk(rootdir):
        dirs[:] = [d for d in dirs if d not in excludes]
        for file in files:
            filepath_norm = os.path.normpath(os.path.join(root, file))
            file_norm = os.path.normpath(file)
            should_exclude = False
            for exclude in excludes:
                if fnmatch.fnmatch(file_norm, exclude):
                    # Skip this file
                    should_exclude = True
                    break
            if should_exclude:
                continue
            if file.endswith(".py"):
                try:
                    s = open(filepath_norm, "r").read()
                except UnicodeDecodeError as e:
                    print(f"Could not read file {file}")
                    print(e)
                    continue
                num_streamlitapps = len(re.findall(r"@[\w]+.streamlit", s))
                num_jobs = len(re.findall(r"@[\w]+.repeat_every", s))
                if num_streamlitapps > 0 or num_jobs > 0:
                    if root != rootdir:
                        init_file = root + "/__init__.py"
                        if os.path.exists(init_file) is False:
                            open(init_file, "a").close()
                    md = filepath_norm
                    md = md.replace("./", "")
                    md = md.replace(".py", "").replace("/", ".")
                    modules_to_import.append(md)
    return modules_to_import


# For a given python file, this returns
# a list with all import statements in that
# file
def get_library_dependencies_for_app(file):
    imports = []
    with open(file, "r") as f:
        for line in f.readlines():
            if "import" in line:
                imports.append(line)
    return imports
