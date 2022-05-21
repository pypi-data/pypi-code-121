import os


def project_to_package(project):
    """
    >>> print(project_to_package('abcdef'))
    abcdef
    >>> print(project_to_package('abc_DEF'))
    abc_DEF
    >>> print(project_to_package('abc-D..EF'))
    abc_D_EF
    """
    tmp = []
    for c in project:
        if 'a' <= c.lower() <= 'z' or c == '_':
            tmp.append(c)
        elif not tmp or tmp[-1] != '_':
            tmp.append('_')
        else:
            pass
    return ''.join(tmp)


def captitalize(s):
    if not s:
        return s
    return s[0].upper() + s[1:]


def camelize(package, upper=True):
    """
    >>> print(camelize('abcdef', False))
    abcdef
    >>> print(camelize('abc_DEF'))
    AbcDEF
    >>> print(camelize('abc_d_efg', False))
    abcDEfg
    """
    tmp = []
    package = package.replace('-', '_')
    for w in package.split('_'):
        tmp.append(captitalize(w))
    if not upper and tmp:
        tmp[0] = tmp[0].lower()
    return ''.join(tmp)


def exe(cmd):
    print(cmd)
    ret = os.system(cmd)
    return ret == 0


def not_ready(cmd):
    return os.system("which " + cmd) != 0


def assert_or_exit(expect, message='failed!'):
    if not expect:
        print(message)
        exit(1)


def dump_file_name(filename: str, project: str):
    if '.' in filename[1:]:
        prefix, suffix = filename.rsplit('.', 1)
        return f'{prefix}.{project}.{suffix}'
    else:
        return f'{filename}.{project}'
