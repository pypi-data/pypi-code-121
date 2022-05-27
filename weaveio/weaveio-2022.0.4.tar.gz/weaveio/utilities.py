import re
import xxhash
import inflect

INFLECTOR = inflect.engine()
PLURAL_DICT = {'spectrum': 'spectra', 'noss': 'nosses', 'use': 'uses'}

def snakecase2camelcase(name):
    """
    Returns a string with underscores between words in camelcase name
    """
    return ''.join(x.capitalize() for x in name.split('_'))


def camelcase2snakecase(name):
    """
    Returns a string with underscores between words in camelcase name
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def make_plural(name):
    if name.endswith('_group'):
        raise ValueError(f"Cannot pluralise {name} since it ends with '_group'")
    for k, v in PLURAL_DICT.items():
        if name.endswith(k):
            return name[:-len(k)] + v
        if name.endswith(v):
            return name + '_group'
    plural_form = INFLECTOR.plural_noun(name)
    single_form = INFLECTOR.singular_noun(name)  # returns False when name is already singular
    if not single_form:
        return plural_form
    return name + '_group'

def make_singular(name):
    if name.endswith('_group'):
        return name[:-len('_group')]
    for v, k in PLURAL_DICT.items():
        if name.endswith(k):
            return name[:-len(k)] + v
        if name.endswith(v):
            return name
    single_form = INFLECTOR.singular_noun(name)  # returns False when name is already singular
    if not single_form:
        return name
    return single_form

class Varname:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

def quote(x):
    """
    Return a quoted string if x is a string otherwise return x
    """
    if isinstance(x, str):
        return f"'{x}'"
    if isinstance(x, Varname):
        return x.name
    return x


def hash_pandas_dataframe(df):
    digester = xxhash.xxh64()
    for i in df.astype(str).values.ravel():
        digester.update(i)
    return digester.hexdigest()


def int_or_none(x):
    if x is None:
        return None
    return int(x)