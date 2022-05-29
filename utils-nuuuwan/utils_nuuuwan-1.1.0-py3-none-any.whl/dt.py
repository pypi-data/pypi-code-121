"""Utils related to simple data types"""
import re


def parse_float(float_str, default=None):
    """Parse float."""
    float_str = float_str.replace(',', '')
    float_str = float_str.replace('-', '0')
    try:
        return (float)(float_str)
    except ValueError:
        return default


def parse_int(int_str, default=None):
    """Parse int."""
    int_str = int_str.replace(',', '')
    int_str = int_str.replace('-', '0')
    try:
        return (int)((float)(int_str))
    except ValueError:
        return default


def to_kebab(s):
    """Convert string to kebab case."""
    s = re.sub(r'[^a-zA-Z0-9]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.replace(' ', '-')
    return s.lower()


def to_snake(s):
    """Convert string to snakes case."""
    return re.sub(r'(\s|-)+', '_', s).lower()


def snake_to_camel(s):
    return s.replace('_', ' ').title().replace(' ', '')


def camel_to_snake(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
