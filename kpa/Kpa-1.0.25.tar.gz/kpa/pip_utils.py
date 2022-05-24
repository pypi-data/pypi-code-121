
import re, json, urllib.request

def check_pkg(pkg, opt, version, line=None):
    '''
    pkg is like "requests"
    opt is like "[security]" or ""
    version is like ">=4.0"
    line is for debugging
    '''
    if opt is None: opt=''
    if version is None: version=''
    try:
        j = json.loads(urllib.request.urlopen('https://pypi.org/pypi/{}/json'.format(pkg)).read())
        latest = j['info']['version']
        v = version.lstrip('~=>')
        update_str = '' if latest == v or latest==v+'.0' or latest.startswith(v) else '>>'
        print('{:<2} {:20} {:10} {:10}'.format(update_str, pkg+opt, version, latest))
    except Exception:
        raise Exception([pkg, opt, version, line])

def check_file(filepath):
    with open(filepath) as f:
        for line in f:
            m = re.match(r'''^\s*'?([-a-zA-Z]+)(\[[a-zA-Z]+\])?([~<>=]{2}[0-9a-zA-Z\.]+)?'?,?\s*$''', line)
            if m:
                pkg, opt, version = m.group(1), m.group(2), m.group(3)
                check_pkg(pkg, opt, version, line)
