from .utils import *
from io import TextIOWrapper
import re
import glob
import os


def format_dart_file_code(path):
    try:
        path = get_path_from_content_root(path)
        os.system("dart format {}".format(path))
        # log("[Formatted] {}".format(path))
    except Exception as e:
        logError(str(e))


def insert_str(string, str_to_insert, index):
    return string[:index] + str_to_insert + string[index:]


def read_dart_file(path):
    try:
        with open(path, "r", encoding="utf8") as file:
            content = file.read()
            return (file, content)
    except Exception as e:
        logError(str(e))
        exit(1)


def write_dart_file(path, content):
    with open(path, "w", encoding="utf8") as file:
        write_content_to_file(file, content)


def write_content_to_file(file: TextIOWrapper, content):
    try:
        file.seek(0)
        file.write(content)
        file.truncate()
        file.close()
    except Exception as e:
        logError(str(e))
        exit(1)


def get_path_from_file(file: TextIOWrapper):
    return file.name.replace("\\", "/")


def get_path_from_content_root(path: str):
    current_working_dictionary = os.path.abspath(
        os.getcwd()).replace("\\", "/")
    return path.replace("\\", "/").replace(current_working_dictionary, "")


def find_dart_files(dir):
    return glob.glob("{}/**/*.dart".format(dir), recursive=True)


def get_dart_class_name(content):
    try:
        regex = r"(?<=class )([\S\s]*?)(?= .*)"
        match = re.findall(regex, content, re.MULTILINE)
        return match and match[0] or ""
    except Exception as e:
        logError(str(e))
        exit(1)


def get_methods_from_string(content):
    regex = r"^(?!  \/\/)(?:.*) (?!_)\w+\([^\(\)]*\)(?= {| async)"
    return re.findall(regex, content, re.MULTILINE)


def get_methods_from_path(path):
    (_, content) = read_dart_file(path)
    return get_methods_from_string(content)


def get_abstract_methods_from_string(content):
    regex = r"\S+ \w+\(.*\);"
    return re.findall(regex, content, re.MULTILINE)


def get_abstract_methods_from_path(path):
    (_, content) = read_dart_file(path)
    return get_abstract_methods_from_string(content)


def get_imports_from_string(content):
    regex = r"import.*;"
    return re.findall(regex, content, re.MULTILINE)


def get_imports_from_path(path):
    (_, content) = read_dart_file(path)
    return get_imports_from_string(content)


def get_mixins_from_string(content):
    reg_exp = r"^(?:class .*UseCase)(?:[^\]]*?)(?:with)([\S\s]*?)(?:implements .*UseCaseType)"
    matches = re.findall(reg_exp, content, re.MULTILINE)
    if matches:
        return list(map(lambda x: x.strip(), matches[0].split(",")))
    else:
        return []


def get_mixins_from_path(path):
    (_, content) = read_dart_file(path)
    return get_mixins_from_string(content)


def insert_dart_file_by_regex(path, regex, replacement):
    try:
        with open(path, "r+", encoding="utf8") as file:
            content = file.read()
            regex = re.compile(regex, flags=re.MULTILINE)
            matches = regex.finditer(content)
            if matches:
                content = insert_str(
                    content, "{}".format(
                        replacement), matches.__next__().span("G1")[1]
                )
            write_content_to_file(file, content)
    except Exception as e:
        logError(str(e))
        exit(1)


def insert_dart_abstract_methods(path, list_method):
    if not list_method:
        return
    regex = r"^(?:abstract class .* ){(?P<G1>(?:.*)||([\r\n]+)||(?:[^\]]*))*?}"
    replacement = "\n  " + "\n  ".join(list_method) + "\n"
    insert_dart_file_by_regex(path, regex, replacement)


def insert_dart_class_methods(path, list_method):
    if not list_method:
        return
    regex = r"^(?:class .* ){(?P<G1>(?:.*)||([\r\n]+)||(?:[^\]]*))}$"
    replacement = "\n  " + "\n  ".join(list_method) + "\n"
    insert_dart_file_by_regex(path, regex, replacement)


def insert_dart_class_mixin(path, list_mixin):
    regex = (
        r"^(?:class .*UseCase)(?P<G1>([^\]]*?)(?:.*)||with (?:.*))(?: implements .*UseCaseType)"
    )
    current_mixins = get_mixins_from_path(path)
    output_mixins = list(set(list_mixin) - set(current_mixins))
    if not output_mixins:
        return
    prefix = ", " if current_mixins else " with "
    replacement = "{}{}".format(prefix, ", ".join(output_mixins))
    insert_dart_file_by_regex(path, regex, replacement)


def insert_dart_imports(path, list_import):
    import_reg_exp = r"import.*;"
    try:
        with open(path, "r+", encoding="utf8") as file:
            content = file.read()
            current_import_files = re.findall(
                import_reg_exp, content, re.MULTILINE)
            new_import_files = "\n".join(
                list(set(list_import) - set(current_import_files))
            )
            if current_import_files:
                last_import = current_import_files[-1]
                content = content.replace(
                    last_import, "{}\n{}".format(last_import, new_import_files)
                )
            else:
                content = new_import_files + "\n" + content
            write_content_to_file(file, content)
    except Exception as e:
        logError(str(e))
        exit(1)
