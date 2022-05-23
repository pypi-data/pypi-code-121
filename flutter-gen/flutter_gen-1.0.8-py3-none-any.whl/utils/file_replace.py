import os
import fileinput
import re

def _update_lines_in_file(operation, file_path):
    for line in fileinput.input([file_path], inplace=True):
        new_line = operation(line)

        if new_line is not None:
            print(operation(line), end='')
        else:
            print(line)

    return [file_path]

def _update_entire_file(operation, file_path):
    try:
        with open(file_path, 'r', errors='ignore') as file:
            contents = file.read()

            new_contents = operation(contents)

            if new_contents is None:
                return []

            if contents == new_contents:
                return []

            with open(file_path, 'w') as file:
                file.write(new_contents)

            return [file_path]
    except:
        print("[Update Entire File] Error")

def _update_single_file(operation, file_path, line_by_line=False):
    if line_by_line:
        return _update_lines_in_file(operation, file_path)
    else:
        return _update_entire_file(operation, file_path)

def _update_directory(operation, path, recursive=False, line_by_line=False,
                      extension=''):
    try:
        files_updated = []
        for name in os.listdir(path):
            full_path = os.path.join(path, name)

            # Ignore directories if not recursive.
            if not recursive and os.path.isdir(full_path):
                continue

            results = update(operation, full_path, recursive, line_by_line,
                            extension)
            files_updated.extend(results)

        return files_updated
    except:
        print("[Update Directory] Error")
        return []

def update(operation, path, recursive=False, line_by_line=False,
           extension=''):
    if not os.path.exists(path):
        raise IOError('Path does not exists: ' + path)

    if not path.endswith(extension):
        return []
        

    if os.path.isfile(path):
        return _update_single_file(operation, path, line_by_line)
    elif os.path.isdir(path):
        return _update_directory(operation, path, recursive, line_by_line,
                                 extension)
    else:
        assert False, 'Path is neither file nor directory.'

def replace(pattern, replacement, path, recursive=False, regex=False,
            extension=''):
    if regex:
        operation = lambda contents: re.sub(pattern, replacement, contents)
    else:
        operation = lambda contents: contents.replace(pattern, replacement)

    return update(operation, path, recursive, False, extension)