import os
import enum

# from pathlib import Path
# import shutils
from .logger import Logger
from .exceptions import DSOException

# def clean_directory(path):
#     for path in Path(path).glob("**/*"):
#         if path.is_file():
#             path.unlink()
#         elif path.is_dir():
#             shutils.rmtree(path)


class SIZE_UNIT(enum.Enum):
    AUTO = 0
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4
    TB = 5

def convert_file_size_unit(size_in_bytes, unit=SIZE_UNIT.AUTO, precision=2):
    if unit == SIZE_UNIT.AUTO:
        if size_in_bytes < 1e3:
            unit = SIZE_UNIT.BYTES
        elif size_in_bytes < 1e6:
            unit = SIZE_UNIT.KB
        elif size_in_bytes < 1e9:
            unit = SIZE_UNIT.GB
        else:
            unit = SIZE_UNIT.TB

    if unit == SIZE_UNIT.BYTES:
        return str(size_in_bytes) + 'B'
    if unit == SIZE_UNIT.KB:
        return str(round(size_in_bytes/1024, precision)) + 'KB'
    elif unit == SIZE_UNIT.MB:
        return str(round(size_in_bytes/(1024*1024), precision)) + 'MB'
    elif unit == SIZE_UNIT.GB:
        return str(round(size_in_bytes/(1024*1024*1024), precision)) + 'GB'
    elif unit == SIZE_UNIT.GB:
        return str(round(size_in_bytes/(1024*1024*1024*1024), precision)) + 'TB'
    else:
        raise NotImplementedError

def is_binary_file(filename):
    """ 
    Return true if the given filename appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    with open(filename, 'rb') as f:
        for block in f:
            if b'\0' in block:
                return True
    return False


def exists_on_path(filename):
    return any([os.path.exists(os.path.join(p, filename)) for p in os.environ.get('PATH', '').split(os.pathsep)])


def render_stream(stream, values):
    if not values: return stream
    import jinja2
    template = jinja2.Environment(undefined=jinja2.StrictUndefined).from_string(stream)
    try:
        rendered = template.render(values)
    except Exception as e:
        Logger.error(f"Failed to render stream.")
        msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
        raise DSOException(msg)

    return rendered


def render_dict_values(dict, values, silent=False):
    if not dict: return dict
    import jinja2, json
    template = jinja2.Environment(undefined=jinja2.StrictUndefined).from_string(json.dumps(dict))
    try:
        rendered = template.render(values)
    except Exception as e:
        if not silent: 
            msg = getattr(e, 'message', getattr(e, 'msg', str(e)))
            Logger.error(f"Render failed: {msg}")
        return dict
    else:
        return json.loads(rendered)


def get_format_from_file_name(file_name):
    from os.path import splitext
    ext = splitext(file_name)[1]
    if ext in ['.yml', '.yaml']:
        return 'yaml'
    elif ext in ['.json', '.csv']:
        return ext[1:]
    else:
        return 'raw'


def load_file(file_path, format='auto', pre_render_values=None):
    if is_binary_file(file_path):
        raise DSOException(f"Cannot load binary file '{file_path}'.")
    
    if format == 'auto':
        format = get_format_from_file_name(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if format == 'raw':
            return render_stream(f.read(), pre_render_values)
        elif format == 'yaml':
            import yaml
            return yaml.safe_load(render_stream(f.read(), pre_render_values)) or {}
        elif format == 'json':
            import json
            return json.loads(render_stream(f.read(), pre_render_values) or '{}') or {}
        elif format == 'csv':
            import csv
            return list(csv.reader(render_stream(f.read(), pre_render_values))) or []
        else:
            raise NotImplementedError



def save_data(data, file_path, format='auto'):
    if format == 'auto':
        format = get_format_from_file_name(file_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        if format == 'yaml':
            import yaml
            yaml.dump(data, f, sort_keys=False, indent=2)
        elif format == 'json':
            import json
            json.dump(data, f, sort_keys=False, indent=2)
        else:
            raise NotImplementedError


def get_file_modified_date(file_path, format='%A, %Y-%m-%d %H:%M:%S'):
    from time import strftime, localtime
    return strftime(format, localtime(os.path.getmtime(file_path)))


def no_enclosing_quotes(value):
    import re
    if re.match(r'^".*"$', value):
        return re.sub(r'^"|"$', '', value)
    elif re.match(r"^'.*'$", value):
        return re.sub(r"^'|'$", '', value)

