
from .operator import (
    lambda_handle,
    lambda_oper,
    lambda_when
)
from collections import namedtuple


def split_by_double_dash(name: str):
    singel_dash = '_'
    double_dash = '__'
    field_name = oper = when = handle = None
    if double_dash in name:
        name = name.split(double_dash)
        if len(name) == 2:
            if name[1].startswith('after') or name[1].startswith('before'):
                field_name = name[0]
                oper = 'eq'
                when, handle = name[1].split(singel_dash)
            else:
                field_name, oper = name
        if len(name) == 3:
            field_name, oper, when_handle = name
            if singel_dash not in when_handle:
                raise ValueError()
            when, handle = when_handle.split(singel_dash)

        if oper not in lambda_oper:
            raise ValueError()

        if when and when not in lambda_when:
            raise ValueError()

        if handle and handle not in lambda_handle:
            raise ValueError()

    else:
        field_name = name
        oper = 'eq'
        when = None
        handle = None
    Name = namedtuple('name', ['field_name', 'oper', 'when', 'handle'])

    return Name(
        field_name,
        oper,
        lambda_when.get(when),
        lambda_handle.get(handle)
    )


def register_method(self, method_name, method):
    setattr(self, method_name, method)


def green(s):
    return '\033[92m' + str(s) + '\033[0m'


def red(s):
    return '\033[31m' + str(s) + '\033[0m'


def convert_to_gff(x):
    ret = []
    for pair in x.split(';'):
        key, value = pair.split(' ')
        ret.append(
            key + '=' + value.strip('"')
        )
    return ';'.join(ret)


def convert_to_gtf(x):
    ret = []
    for pair in x.split(';'):
        key, value = pair.split('=')
        ret.append(
            key + ' ' + '"' + value.strip('"') + '"'
        )
    return ';'.join(ret)


if __name__ == '__main__':
    name1 = 'type'
    name2 = 'type__eq'
    name3 = 'type__eq__after_lower'
    print(split_by_double_dash(name1).field_name)
    print(split_by_double_dash(name2))
    print(split_by_double_dash(name3))
