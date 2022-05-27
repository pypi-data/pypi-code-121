import hashlib
import os

from datetime import datetime
from random import randint


def absolute_path(dir_path):
    """Return absolute path"""
    return os.path.abspath(os.path.expanduser(os.path.expandvars(dir_path)))


def yes_or_no(question):
    """Prompt for yes/no question"""
    while True:
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply in ['y', 'yes']:
            return True
        if reply in ['n', 'no']:
            return False


def that():
    """Tribute to this.py and Laozi"""
    s = """Tao Te Ching / Chapter 45
    Great support seems deficient,
    Employed it will not collapse;
    Great buoyancy seems empty,
    Utilized it will not be exhausted.
    Great honesty seems corrupt,
    Great skills seem incompetent,
    Great orations seem inarticulate.
    Movement overcomes coldness,
    Stillness overcomes heat,
    Tranquility makes the world become righteous."""
    # https://en.wikisource.org/wiki/Translation:Tao_Te_Ching
    # Creative Commons Attribution-ShareAlike License

    d = {}
    for c in (65, 97):
        for i in range(26):
            d[chr(i+c)] = chr((i+13) % 26 + c)

    return "".join([d.get(c, c) for c in s if c.isalnum()])


def generate_sid(args, other_args):
    """Generate a session ID"""
    s = that()
    # Three and seven are magic numbers
    hlen = 3
    tlen = 4
    n = randint(0, len(s)-hlen)
    now = datetime.now().isoformat()
    head = ''.join(list(s)[n:n+hlen]).lower()
    tail = hashlib.sha256(bytes(now, 'utf-8')).hexdigest()[0:tlen]
    print(head + tail)
